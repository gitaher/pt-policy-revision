"""Deterministic checks: independent oracle, no LLM, network, clock or writes."""

from .checks import equivalent, expected, plain, validate, verdict


def verify_input(tool, value):
    if tool != "compute":
        return verdict(False, "unknown tool")
    try:
        validate(plain(value))
        return verdict(True, "valid task input")
    except (ValueError, TypeError, KeyError, OverflowError, AttributeError):
        return verdict(False, "invalid task input")


def verify_output(tool, input_value, output_value, workspace):
    before = verify_input(tool, input_value)
    if not before["valid"]:
        return before
    try:
        actual, wanted = plain(output_value), expected(plain(input_value))
        valid = equivalent(actual, wanted)
        return verdict(valid, "matches independent oracle" if valid else "incorrect or incomplete output")
    except (ValueError, TypeError, KeyError, OverflowError, AttributeError):
        return verdict(False, "malformed output")


def verify_task(task, arguments, output, reference, workspace):
    if task != "revise-policy":
        return verdict(False, "unknown task")
    return verify_output("compute", arguments, output, workspace)
