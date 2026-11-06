"""Structured tool and task contracts; declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    COMPUTE = "compute"


class Task(Enum):
    RUN = "revise-policy"


@dataclass
class Feedback(Output):
    id: Annotated[str, "Unique feedback ID"]
    strength: Annotated[int, "Integer confidence from 0 through 100"]
    correct: Annotated[bool, "Whether the directional forecast was correct"]
    decided_at: Annotated[str, "Forecast timestamp"]
    resolved_at: Annotated[str, "Outcome availability timestamp"]
    split: Annotated[str, "calibration or holdout"]


@dataclass
class Loss(Output):
    threshold: Annotated[int, "Candidate threshold"]
    cost: Annotated[int, "Total mature calibration cost"]


@dataclass
class TaskInput(Output):
    feedback: Annotated[list[Feedback], "Frozen outcome feedback"]
    cutoff: Annotated[str, "Inclusive revision timestamp"]
    candidates: Annotated[list[int], "Unique thresholds 0 through 101; 101 always abstains"]
    current_threshold: Annotated[int, "Current threshold, must be a candidate"]


@dataclass
class TaskOutput(Output):
    chosen_threshold: Annotated[int, "Minimum cost; ties minimize change then threshold"]
    losses: Annotated[list[Loss], "Costs in ascending threshold order"]
    evidence_ids: Annotated[list[str], "Sorted mature calibration feedback IDs"]


TOOLS = {Tool.COMPUTE: (TaskInput, TaskOutput)}
TASKS = {Task.RUN: (TaskInput, TaskOutput)}
