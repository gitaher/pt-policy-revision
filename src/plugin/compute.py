from dataclasses import asdict
from pathlib import Path

from slimconfig import build_output

from contract import TaskInput, TaskOutput
from plugin.logic import solve
from verifier import verify_input


def compute(value: TaskInput, workspace: Path) -> TaskOutput:
    check = verify_input("compute", value)
    if not check["valid"]:
        raise ValueError(check["message"])
    return build_output(solve(asdict(value)), TaskOutput)
