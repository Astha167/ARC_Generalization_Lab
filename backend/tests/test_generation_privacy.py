import json
import os
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import app


class GenerationPrivacyAndExperimentTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_generate_does_not_expose_test_outputs(self):
        resp = self.client.post("/api/tasks/generate", json={"count": 1, "mode": "standard"})
        self.assertEqual(resp.status_code, 200, resp.text)
        payload = resp.json()
        self.assertIn("task_id", payload)
        self.assertIn("train", payload)
        self.assertIn("test", payload)
        for pair in payload["test"]:
            self.assertNotIn("output", pair)
            self.assertIn("input", pair)

    def test_experiment_run_saves_measured_result(self):
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 4, "fresh_count": 3, "solver": "heuristic", "mode": "standard"},
        )
        self.assertEqual(resp.status_code, 200, resp.text)
        payload = resp.json()
        self.assertIn("public", payload)
        self.assertIn("fresh", payload)
        self.assertIn("gap", payload)
        self.assertIn("distribution", payload)
        self.assertTrue(payload["public"]["task_count"] > 0)
        self.assertTrue(payload["fresh"]["task_count"] > 0)

        results_dir = Path(__file__).resolve().parents[2] / "experiments" / "results"
        self.assertTrue(results_dir.exists())
        saved_files = list(results_dir.glob("*.json"))
        self.assertTrue(saved_files)


if __name__ == "__main__":
    unittest.main()
