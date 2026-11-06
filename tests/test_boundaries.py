import copy
import unittest

import test_verifier as helpers

from plugin.logic import solve
from verifier import verify_input


class BoundaryTests(unittest.TestCase):
    setUp = helpers.VerifierTests.setUp
    check = helpers.VerifierTests.check

    def reject(self, x):
        self.assertFalse(verify_input("compute", x)["valid"])

    def accept(self, x, gold):
        self.assertTrue(self.check(gold, x))
        self.assertEqual(solve(x), gold)

    def test_no_feedback_preserves_current(self):
        self.accept(
            dict(self.x, feedback=[]),
            {"chosen_threshold": 0, "losses": [{"threshold": t, "cost": 0} for t in [0, 50, 101]], "evidence_ids": []},
        )

    def test_threshold_equality_executes_forecast(self):
        x = copy.deepcopy(self.x)
        x["feedback"] = x["feedback"][:1]
        x["feedback"][0]["strength"] = 50
        self.accept(
            x,
            {
                "chosen_threshold": 101,
                "losses": [{"threshold": 0, "cost": 3}, {"threshold": 50, "cost": 3}, {"threshold": 101, "cost": 1}],
                "evidence_ids": ["f1"],
            },
        )

    def test_future_feedback_does_not_change_policy(self):
        x = copy.deepcopy(self.x)
        x["feedback"][2]["strength"] = 0
        x["feedback"][2]["correct"] = True
        self.accept(x, self.gold)

    def test_holdout_labels_cannot_change_policy(self):
        x = copy.deepcopy(self.x)
        x["feedback"][3]["correct"] = True
        x["feedback"][3]["strength"] = 0
        self.accept(x, self.gold)

    def test_cutoff_is_inclusive(self):
        x = copy.deepcopy(self.x)
        x["feedback"][0]["resolved_at"] = x["cutoff"]
        self.accept(x, self.gold)

    def test_equal_loss_prefers_nearer_current(self):
        x = dict(self.x, feedback=self.x["feedback"][1:2], current_threshold=50)
        self.accept(
            x,
            {
                "chosen_threshold": 50,
                "losses": [{"threshold": 0, "cost": 0}, {"threshold": 50, "cost": 0}, {"threshold": 101, "cost": 1}],
                "evidence_ids": ["f2"],
            },
        )

    def test_ties_equal_distance_choose_smaller(self):
        rows = [
            dict(self.x["feedback"][0], id="a", strength=20, correct=True),
            dict(self.x["feedback"][0], id="b", strength=20, correct=True),
            dict(self.x["feedback"][0], id="c", strength=30, correct=False),
        ]
        x = dict(self.x, feedback=rows, candidates=[20, 30, 40], current_threshold=30)
        self.accept(
            x,
            {
                "chosen_threshold": 20,
                "losses": [{"threshold": 20, "cost": 3}, {"threshold": 30, "cost": 5}, {"threshold": 40, "cost": 3}],
                "evidence_ids": ["a", "b", "c"],
            },
        )

    def test_permutation_invariance(self):
        self.accept(dict(self.x, feedback=list(reversed(self.x["feedback"])), candidates=[101, 50, 0]), self.gold)

    def test_invalid_candidates(self):
        for c in [[], [0, 0], [True, 50], [-1, 0], [0, 102]]:
            self.reject(dict(self.x, candidates=c))
        self.reject(dict(self.x, current_threshold=2))

    def test_invalid_feedback_labels(self):
        for k, v in [("correct", 1), ("split", "test"), ("strength", 101), ("resolved_at", "2025-12-31T00:00:00Z")]:
            x = copy.deepcopy(self.x)
            x["feedback"][0][k] = v
            self.reject(x)
