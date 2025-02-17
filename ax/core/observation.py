#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

import json
from copy import deepcopy
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from ax.core.arm import Arm
from ax.core.base import Base
from ax.core.data import Data
from ax.core.experiment import Experiment
from ax.core.types import TParameterization


class ObservationFeatures(Base):
    """The features of an observation.

    These include both the arm parameters and the features of the
    observation found in the Data object: trial index, times,
    and random split. This object is meant to contain everything needed to
    represent this observation in a model feature space. It is essentially a
    row of Data joined with the arm parameters.

    An ObservationFeatures object would typically have a corresponding
    ObservationData object that provides the observed outcomes.

    Attributes:
        parameters: arm parameters
        trial_index: trial index
        start_time: batch start time
        end_time: batch end time
        random_split: random split

    """

    def __init__(
        self,
        parameters: TParameterization,
        trial_index: Optional[np.int64] = None,
        start_time: Optional[pd.Timestamp] = None,
        end_time: Optional[pd.Timestamp] = None,
        random_split: Optional[np.int64] = None,
    ) -> None:
        self.parameters = parameters
        self.trial_index = trial_index
        self.start_time = start_time
        self.end_time = end_time
        self.random_split = random_split

    @staticmethod
    def from_arm(
        arm: Arm,
        trial_index: Optional[np.int64] = None,
        start_time: Optional[pd.Timestamp] = None,
        end_time: Optional[pd.Timestamp] = None,
        random_split: Optional[np.int64] = None,
    ) -> "ObservationFeatures":
        """Convert a Arm to an ObservationFeatures, including additional
        data as specified.
        """
        return ObservationFeatures(
            parameters=arm.parameters,
            trial_index=trial_index,
            start_time=start_time,
            end_time=end_time,
            random_split=random_split,
        )

    def update_features(
        self, new_features: "ObservationFeatures"
    ) -> "ObservationFeatures":
        """Updates the existing ObservationFeatures with the fields of the the input.

        Adds all of the new parameters to the existing parameters and overwrites
        any other fields that are not None on the new input features."""
        self.parameters.update(new_features.parameters)
        if new_features.trial_index is not None:
            self.trial_index = new_features.trial_index
        if new_features.start_time is not None:
            self.start_time = new_features.start_time
        if new_features.end_time is not None:
            self.end_time = new_features.end_time
        if new_features.random_split is not None:
            self.random_split = new_features.random_split
        return self

    def __repr__(self) -> str:
        strs = []
        for attr in ["trial_index", "start_time", "end_time", "random_split"]:
            if getattr(self, attr) is not None:
                strs.append(", {attr}={val}".format(attr=attr, val=getattr(self, attr)))
        repr_str = "ObservationFeatures(parameters={parameters}".format(
            parameters=self.parameters
        )
        repr_str += "".join(strs) + ")"
        return repr_str

    def __hash__(self) -> int:
        parameters = self.parameters.copy()
        for k, v in parameters.items():
            if type(v) is np.int64:
                parameters[k] = int(v)  # pragma: no cover
            elif type(v) is np.float32:
                parameters[k] = float(v)  # pragma: no cover
        return hash(
            (
                json.dumps(parameters, sort_keys=True),
                self.trial_index,
                self.start_time,
                self.end_time,
                self.random_split,
            )
        )


class ObservationData(Base):
    """Outcomes observed at a point.

    The "point" corresponding to this ObservationData would be an
    ObservationFeatures object.

    Attributes:
        metric_names: A list of k metric names that were observed
        means: a k-array of observed means
        covariance: a (k x k) array of observed covariances
    """

    def __init__(
        self, metric_names: List[str], means: np.ndarray, covariance: np.ndarray
    ) -> None:
        k = len(metric_names)
        if means.shape != (k,):
            raise ValueError(
                "Shape of means should be {}, is {}.".format((k,), (means.shape))
            )
        if covariance.shape != (k, k):
            raise ValueError(
                "Shape of covariance should be {}, is {}.".format(
                    (k, k), (covariance.shape)
                )
            )
        self.metric_names = metric_names
        self.means = means
        self.covariance = covariance

    def __repr__(self) -> str:
        return "ObservationData(metric_names={mn}, means={m}, covariance={c})".format(
            mn=self.metric_names, m=self.means, c=self.covariance
        )


class Observation(Base):
    """Represents an observation.

    A set of features (ObservationFeatures) and corresponding measurements
    (ObservationData). Optionally, a arm name associated with the
    features.

    Attributes:
        features (ObservationFeatures)
        data (ObservationData)
        arm_name (Optional[str])
    """

    def __init__(
        self,
        features: ObservationFeatures,
        data: ObservationData,
        arm_name: Optional[str] = None,
    ) -> None:
        self.features = features
        self.data = data
        self.arm_name = arm_name


def observations_from_data(experiment: Experiment, data: Data) -> List[Observation]:
    """Convert Data to observations.

    Converts a Data object to a list of Observation objects. Pulls
    arm parameters from experiment.  Overrides fidelity parameters in the arm
    with those found in the Data object.

    Uses a diagonal covariance matrix across metric_names.

    Args:
        experiment: Experiment with arm parameters.
        data: Data of observations

    Returns: List of Observation objects.
    """
    feature_cols = list(
        {
            "arm_name",
            "trial_index",
            "start_time",
            "end_time",
            "random_split",
            "fidelities",
        }.intersection(data.df.columns)
    )
    observations = []
    for g, d in data.df.groupby(by=feature_cols):
        # If g were a single value, zip would transform it into an index,
        # and we want the value.
        if not isinstance(g, (list, tuple)):
            g = [g]  # pragma: no cover
        features = dict(zip(feature_cols, g))
        obs_kwargs = {}
        obs_parameters = experiment.arms_by_name[features["arm_name"]].parameters.copy()
        if obs_parameters:
            obs_kwargs["parameters"] = obs_parameters
        for f in ["trial_index", "start_time", "end_time", "random_split"]:
            obs_kwargs[f] = features.get(f, None)
        if "fidelities" in features:
            fidelity_dict = json.loads(features["fidelities"])
            for param_name, val in fidelity_dict.items():
                obs_parameters[param_name] = val
        observations.append(
            Observation(
                features=ObservationFeatures(**obs_kwargs),
                data=ObservationData(
                    metric_names=list(d["metric_name"].values),
                    means=d["mean"].values,
                    covariance=np.diag(d["sem"].values ** 2),
                ),
                arm_name=features["arm_name"],
            )
        )

    return observations


def separate_observations(
    observations: List[Observation], copy: bool = False
) -> Tuple[List[ObservationFeatures], List[ObservationData]]:
    """Split out observations into features+data.

    Args:
        observations: input observations

    Returns:
        observation_features: ObservationFeatures
        observation_data: ObservationData
    """
    if copy:
        observation_features = [deepcopy(obs.features) for obs in observations]
        observation_data = [deepcopy(obs.data) for obs in observations]
    else:
        observation_features = [obs.features for obs in observations]
        observation_data = [obs.data for obs in observations]
    return observation_features, observation_data
