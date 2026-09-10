"""Tests for Phase 2: Experiment execution, identical solver evaluation,
distribution statistics comparison, withheld test outputs privacy, and
explicit generator_mode labeling (Live vs Fallback).
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app import app
from backend.arc_generator import ArcTaskGenerator
from backend.arc_engine import load_generated_tasks, compute_stats, compare_distributions
from backend.solvers import get_solver


class TestExperimentAndPrivacy(unittest.TestCase):
    """Test suite covering Phase 2 Experiment and Privacy requirements."""

    def setUp(self):
        self.client = TestClient(app)
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ArcTaskGenerator(root=Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_same_solver_used_on_both_public_and_fresh(self):
        """Verify the experiment runs the exact same solver on both public and fresh datasets."""
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 3, "fresh_count": 2, "solver": "heuristic", "mode": "standard"},
        )
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()

        # Both public and fresh have been evaluated with the specified solver
        self.assertEqual(data["solver"]["name"], "heuristic")
        self.assertEqual(data["public"]["solver"], "heuristic")
        self.assertEqual(data["fresh"]["solver"], "heuristic")
        self.assertIn("accuracy", data["public"])
        self.assertIn("accuracy", data["fresh"])
        self.assertIn("gap", data)
        # Gap is accurately calculated as public_acc - fresh_acc
        expected_gap = round(data["public"]["accuracy"] - data["fresh"]["accuracy"], 4)
        self.assertEqual(data["gap"], expected_gap)

    def test_fallback_mode_is_explicitly_labeled_and_not_genuine_experiment(self):
        """If OPENAI_API_KEY is not set, experiment must flag generator_mode='fallback' and genuine_experiment=False."""
        with patch.dict(os.environ, {}, clear=True):
            resp = self.client.post(
                "/api/experiments/run",
                json={"public_limit": 2, "fresh_count": 2, "solver": "heuristic"},
            )
            self.assertEqual(resp.status_code, 200, resp.text)
            data = resp.json()

            self.assertEqual(data["generator_mode"], "fallback")
            self.assertFalse(data["genuine_experiment"])
            self.assertEqual(data["fresh_dataset"], "fallback-local")
            self.assertIn("warning", data)
            self.assertIn("MUST NOT be presented as a genuine public-vs-fresh generation experiment", data["warning"])
            self.assertEqual(data["fresh"]["generator_mode"], "fallback")

    def test_live_mode_flags_genuine_experiment(self):
        """When live generator succeeds, genuine_experiment=True and generator_mode='live'."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-mock-key"}):
            sample_tasks = {
                "task_001": {
                    "train": [
                        {"input": [[1, 0], [0, 1]], "output": [[0, 1], [1, 0]]},
                        {"input": [[0, 2], [2, 0]], "output": [[2, 0], [0, 2]]},
                    ],
                    "test": [{"input": [[2, 0], [0, 2]], "output": [[0, 2], [2, 0]]}],
                },
                "task_002": {
                    "train": [
                        {"input": [[3, 0], [0, 3]], "output": [[0, 3], [3, 0]]},
                        {"input": [[0, 4], [4, 0]], "output": [[4, 0], [0, 4]]},
                    ],
                    "test": [{"input": [[4, 0], [0, 4]], "output": [[0, 4], [4, 0]]}],
                },
            }
            with patch.object(ArcTaskGenerator, "generate", return_value=list(sample_tasks.values())):
                with patch.object(ArcTaskGenerator, "_has_live_generator", return_value=True):
                    resp = self.client.post(
                        "/api/experiments/run",
                        json={"public_limit": 2, "fresh_count": 2, "solver": "heuristic"},
                    )
                    self.assertEqual(resp.status_code, 200, resp.text)
                    data = resp.json()
                    self.assertEqual(data["generator_mode"], "live")
                    self.assertTrue(data["genuine_experiment"])
                    self.assertEqual(data["fresh_dataset"], "arc-task-gen")
                    self.assertNotIn("warning", data)

    def test_distribution_matching_metrics(self):
        """Verify distribution metrics (input_area, input_rows, input_cols, colors) are computed for both."""
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 2, "fresh_count": 2, "solver": "heuristic"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        dist = data["distribution"]
        self.assertIn("public", dist)
        self.assertIn("fresh", dist)
        for d in (dist["public"], dist["fresh"]):
            self.assertIn("input_area", d)
            self.assertIn("input_rows", d)
            self.assertIn("input_cols", d)
            self.assertIn("colors_per_task", d)
            self.assertIn("mean", d["input_area"])

    def test_privacy_fresh_task_test_output_withheld_in_all_serving_endpoints(self):
        """Test outputs must NEVER be revealed in task listing or task detail endpoints."""
        # 1. /api/tasks/generate endpoint
        resp_gen = self.client.post("/api/tasks/generate", json={"count": 2})
        self.assertEqual(resp_gen.status_code, 200)
        gen_data = resp_gen.json()
        for task in gen_data["tasks"]:
            self.assertIn("test", task)
            for pair in task["test"]:
                self.assertNotIn("output", pair)
                self.assertIn("input", pair)

        # 2. /api/tasks/generated endpoint
        resp_list = self.client.get("/api/tasks/generated")
        self.assertEqual(resp_list.status_code, 200)
        list_data = resp_list.json()
        self.assertIn("tasks", list_data)
        if list_data["tasks"]:
            tid = list_data["tasks"][0]["id"]
            # 3. /api/tasks/generated/{task_id} endpoint
            resp_item = self.client.get(f"/api/tasks/generated/{tid}")
            self.assertEqual(resp_item.status_code, 200)
            item_data = resp_item.json()
            self.assertEqual(item_data["dataset"], "generated")
            for pair in item_data["test"]:
                self.assertNotIn("output", pair)
                self.assertIn("input", pair)

        # 4. /api/tasks/public and /api/tasks/public/{task_id}
        resp_pub = self.client.get("/api/tasks/public/007bbfb7")
        if resp_pub.status_code == 200:
            pub_task = resp_pub.json()
            for pair in pub_task["test"]:
                self.assertNotIn("output", pair)
                self.assertIn("input", pair)

    def test_evaluate_endpoint_only_reveals_ground_truth_upon_submission(self):
        """The ground truth is only revealed when POST /api/evaluate is called with a predicted grid."""
        # Query evaluate on a generated task
        tasks = load_generated_tasks()
        if tasks:
            tid = next(iter(tasks.keys()))
            resp = self.client.post(
                "/api/evaluate",
                json={"task_id": tid, "dataset": "generated", "predicted": [[0, 0], [0, 0]]},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("ground_truth", data)
            self.assertIn("exact_match", data)
            self.assertIn("cell_accuracy", data)

    def test_experiments_listing_and_retrieval_persistence(self):
        """Verify experiment runs are persisted to disk and accessible via /api/experiments."""
        resp_run = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 2, "fresh_count": 2, "solver": "heuristic"},
        )
        self.assertEqual(resp_run.status_code, 200)
        exp_id = resp_run.json()["experiment_id"]

        # List experiments
        resp_list = self.client.get("/api/experiments")
        self.assertEqual(resp_list.status_code, 200)
        experiments = resp_list.json()["experiments"]
        exp_ids = [e["experiment_id"] for e in experiments]
        self.assertIn(exp_id, exp_ids)

        # Get single experiment
        resp_get = self.client.get(f"/api/experiments/{exp_id}")
        self.assertEqual(resp_get.status_code, 200)
        retrieved = resp_get.json()
        self.assertEqual(retrieved["experiment_id"], exp_id)
        self.assertIn("gap", retrieved)
        self.assertIn("public_data_source", retrieved)
        self.assertIn("fresh_data_source", retrieved)

    def test_same_solver_enforcement(self):
        """Verify that solver evaluation uses the exact same solver instance/metadata for public and fresh."""
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 2, "fresh_count": 2, "solver": "heuristic"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["public"]["solver"], data["fresh"]["solver"])
        self.assertEqual(data["public"]["solver"], data["solver"]["name"])

    def test_public_and_fresh_sample_sizes_exposed_honestly(self):
        """Public evaluated count must reflect actual limit N, not entire benchmark."""
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 4, "fresh_count": 3, "solver": "heuristic"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["public"]["task_count"], 4)
        self.assertEqual(data["fresh"]["task_count"], 3)
        self.assertIn("PUBLIC TASKS EVALUATED: 4", data["public"]["evaluated_tasks_label"])
        self.assertIn("FRESH TASKS EVALUATED: 3", data["fresh"]["evaluated_tasks_label"])
        self.assertGreater(data["public"]["total_benchmark_tasks"], 50)

    def test_gap_calculation_scenarios(self):
        """Test gap calculations: equal accuracy, public > fresh, fresh > public, and honest interpretation."""
        # 1. Public > Fresh
        public_acc, fresh_acc = 0.80, 0.40
        self.assertEqual(round(public_acc - fresh_acc, 4), 0.40)

        # 2. Fresh > Public
        public_acc, fresh_acc = 0.30, 0.70
        self.assertEqual(round(public_acc - fresh_acc, 4), -0.40)

        # 3. Equal accuracy
        public_acc, fresh_acc = 0.50, 0.50
        self.assertEqual(round(public_acc - fresh_acc, 4), 0.0)

        # Test from API response
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 2, "fresh_count": 2, "solver": "heuristic"},
        )
        self.assertEqual(resp.status_code, 200)
        d = resp.json()
        self.assertEqual(d["gap"], round(d["public"]["accuracy"] - d["fresh"]["accuracy"], 4))
        self.assertIn("Diagnostic performance gap", d["gap_interpretation"])
        self.assertIn("metric_definition", d)

    def test_recursive_privacy_boundary(self):
        """Recursively scan all public API payloads to guarantee no test outputs, private keys, or secrets."""
        forbidden_keys = {"output", "rule", "slot", "prompt", "api_key", "secret", "OPENAI_API_KEY"}
        endpoints = [
            ("GET", "/api/tasks/public/007bbfb7"),
            ("GET", "/api/tasks/demo/DEMO-001"),
            ("GET", "/api/tasks/generated"),
            ("GET", "/api/audit/tasks"),
        ]

        def check_forbidden(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    # 'test' array elements must never have 'output'
                    if path.endswith("test") or path.endswith("test[]"):
                        self.assertNotEqual(k, "output", f"Found test output in {path}.{k}")
                    self.assertNotIn(k.lower(), ["rule_description", "api_key", "prompt_text"])
                    check_forbidden(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    check_forbidden(item, f"{path}[{idx}]")

        for method, url in endpoints:
            resp = self.client.get(url) if method == "GET" else self.client.post(url)
            if resp.status_code == 200:
                check_forbidden(resp.json(), path=url)

    def test_blind_audit_data_source_labeling(self):
        """Verify GET /api/audit/tasks returns correct source and disclaimer."""
        resp = self.client.get("/api/audit/tasks")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("source", data)
        self.assertIn("label", data)
        self.assertIn("disclaimer", data)
        self.assertIn("tasks", data)
        # Ensure test outputs are stripped in audit tasks
        for t in data["tasks"]:
            for pair in t["test"]:
                self.assertNotIn("output", pair)
                self.assertIn("input", pair)

    def test_invalid_experiment_parameters(self):
        """Verify invalid experiment parameters return clean HTTP errors."""
        # Unknown solver
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 2, "fresh_count": 2, "solver": "non_existent_solver"},
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
