"""Runnable with unittest offline; pytest also discovers these tests."""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from plugin.logic import solve
from verifier import verify_input, verify_output, verify_task
from verifier.checks import equivalent


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / "tests" / "fixture.json").read_text())
        self.x, self.gold = self.fixture["input"], self.fixture["gold"]

    def check(self, out, x=None):
        return verify_task("revise-policy", self.x if x is None else x, out, None, ROOT)["valid"]

    def test_correct_hand_computed_gold(self):
        self.assertTrue(self.check(self.gold))

    def test_tool_matches_hand_computed_gold(self):
        self.assertTrue(equivalent(solve(self.x), self.gold))

    def test_wrong_value(self):
        out = copy.deepcopy(self.gold)
        key = next(iter(out))
        out[key] = [] if not isinstance(out[key], list) else ["invented"]
        self.assertFalse(self.check(out))
        # Also reject a well-shaped but semantically wrong answer.
        out = copy.deepcopy(self.gold)
        if isinstance(out[key], list):
            out[key] = []
        elif key == "chosen_threshold":
            out[key] = self.x["current_threshold"]
        else:
            out[key] += 1
        self.assertFalse(self.check(out))

    def test_missing_output(self):
        self.assertFalse(self.check(None))

    def test_missing_field(self):
        self.assertFalse(self.check({}))

    def test_extra_field(self):
        self.assertFalse(self.check(dict(self.gold, invented=0)))

    def test_malformed_scalar(self):
        self.assertFalse(self.check("not JSON object"))

    def test_nonfinite(self):
        self.assertFalse(self.check({k: float("nan") for k in self.gold}))

    def test_determinism(self):
        a = verify_output("compute", self.x, self.gold, ROOT)
        self.assertEqual(a, verify_output("compute", self.x, self.gold, ROOT))

    def test_unknown_dispatch(self):
        self.assertFalse(verify_task("unknown", self.x, self.gold, None, ROOT)["valid"])
        self.assertFalse(verify_input("unknown", self.x)["valid"])

    def test_missing_input(self):
        self.assertFalse(verify_input("compute", {})["valid"])

    def test_contract_roundtrip_when_dependencies_available(self):
        try:
            from slimconfig import build_output, plain_output
        except ImportError:
            self.skipTest("slimconfig unavailable offline; run uv sync --extra dev")
        from contract import TaskInput, TaskOutput

        x = build_output(self.x, TaskInput)
        out = build_output(self.gold, TaskOutput)
        self.assertTrue(self.check(out, x))
        self.assertTrue(equivalent(plain_output(out), self.gold))
        from plugin.compute import compute

        self.assertTrue(self.check(compute(x, ROOT), x))


if __name__ == "__main__":
    unittest.main()
