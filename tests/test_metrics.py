"""Sanity tests for the metrics module. Run: python -m unittest discover tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decisionarena import metrics  # noqa: E402


class TestMetrics(unittest.TestCase):
    def test_ece_perfectly_calibrated(self):
        # every prediction of 1.0 is correct -> confidence == accuracy -> ECE 0
        self.assertAlmostEqual(metrics._ece([1.0, 1.0], [1, 1]), 0.0)
        # every prediction of 0.0 is wrong -> ECE 1
        self.assertAlmostEqual(metrics._ece([0.0, 0.0], [1, 1]), 1.0)

    def test_brier_bounds(self):
        self.assertAlmostEqual(metrics._brier([1.0, 0.0], [1, 0]), 0.0)
        self.assertAlmostEqual(metrics._brier([0.0, 1.0], [1, 0]), 1.0)

    def test_label_agreement(self):
        a = {"q": {"kind": "choice", "value": "x", "probabilities": {"x": 0.9}, "confidence": 0.9}}
        b = {"q": {"kind": "choice", "value": "x", "probabilities": {"x": 0.7}, "confidence": 0.7}}
        c = {"q": {"kind": "choice", "value": "y", "probabilities": {"y": 0.6}, "confidence": 0.6}}
        self.assertEqual(metrics.label_agreement(a, b)["rate"], 1.0)
        self.assertEqual(metrics.label_agreement(a, c)["rate"], 0.0)

    def test_noul_agreement_uses_the_half_side(self):
        a = {"q": {"kind": "noul", "value": 0.51, "probabilities": {}, "confidence": None}}
        b = {"q": {"kind": "noul", "value": 0.80, "probabilities": {}, "confidence": None}}
        self.assertEqual(metrics.label_agreement(a, b)["rate"], 1.0)

    def test_action_change_rate(self):
        a = {"q": {"kind": "noul", "value": 0.9, "probabilities": {}, "confidence": None}}
        b = {"q": {"kind": "noul", "value": 0.2, "probabilities": {}, "confidence": None}}
        r = metrics.action_change_rate(a, b, {"q": 0.5})
        self.assertEqual(r["action_changes"], 1)
        self.assertEqual(r["action_change_rate"], 1.0)

    def test_score_case_pulls_probability_from_the_gold_level(self):
        answers = {"sev": {"kind": "score", "value": 2.0,
                           "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7}, "confidence": 0.7}}
        s = metrics.score_case(answers, {"sev": 2})
        self.assertEqual(s["rows"][0]["correct"], True)
        self.assertAlmostEqual(s["rows"][0]["p_gold"], 0.7)

    def test_reliability_bins_do_not_lose_points(self):
        probs = [0.05, 0.15, 0.45, 0.55, 0.95]
        outs = [0, 0, 0, 1, 1]
        bins = metrics.reliability_bins(probs, outs)
        self.assertEqual(sum(b["n"] for b in bins), len(probs))


if __name__ == "__main__":
    unittest.main()
