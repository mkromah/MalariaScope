import unittest
from scripts.dashboard_logic import classify_cell, compare_scores

class DecisionTests(unittest.TestCase):
    def test_frozen_margin(self):
        self.assertEqual(classify_cell(0.001, 0.49)[0], "uninfected")
        self.assertEqual(classify_cell(0.999, 0.49)[0], "parasitized")
        self.assertEqual(classify_cell(0.5, 0.49)[0], "review")
        self.assertEqual(classify_cell(0.5-0.49, 0.49)[0], "review")
        self.assertEqual(classify_cell(0.5+0.49, 0.49)[0], "review")

    def test_invalid_values_fail(self):
        for v in [-0.1, 1.1, float("nan")]:
            with self.assertRaises(ValueError):
                classify_cell(v, 0.49)
        with self.assertRaises(ValueError):
            classify_cell(0.5, 0.5)

    def test_comparison_is_not_clinical(self):
        diff = compare_scores({"score": 0.9, "category": "parasitized"},
                              {"score": 0.1, "category": "uninfected"})
        self.assertAlmostEqual(diff["difference_percentage_points"], 80.0)
        self.assertIn("not evidence", diff["notice"])

if __name__ == "__main__":
    unittest.main()
