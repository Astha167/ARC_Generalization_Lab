"""Tests for arc-task-gen adapter, verification of environment handling,
error handling, output synchronization, and privacy.
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
from backend.arc_engine import load_generated_tasks, validate_task


class TestGeneratorAdapter(unittest.TestCase):
    """Test suite for backend/arc_generator.py and the generation pipeline."""

    def setUp(self):
        self.client = TestClient(app)
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ArcTaskGenerator(root=Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_adapter_initialization(self):
        """A: Adapter initializes with correct paths and defaults."""
        self.assertIsNotNone(self.generator)
        self.assertEqual(self.generator.root, Path(self.temp_dir))
        self.assertEqual(self.generator.generations_dir, Path(self.temp_dir) / "data" / "generations")
        self.assertIn(self.generator.generator_mode, {"live", "fallback"})

    def test_missing_api_key_triggers_fallback(self):
        """B & C: When OPENAI_API_KEY is not set, generator gracefully uses fallback."""
        with patch.dict(os.environ, {}, clear=True):
            gen = ArcTaskGenerator(root=Path(self.temp_dir))
            self.assertFalse(gen._has_live_generator())
            self.assertEqual(gen.generator_mode, "fallback")
            tasks = gen.generate(2, mode="standard")
            self.assertEqual(len(tasks), 2)
            self.assertEqual(gen.generator_mode, "fallback")
            self.assertTrue(gen.run_id.startswith("fallback_"))

    def test_environment_variable_passthrough(self):
        """B: Ensure OPENAI_BASE_URL, ARCGEN_MODEL, etc. are passed to upstream env."""
        mock_env = {
            "OPENAI_API_KEY": "sk-test-key-12345",
            "OPENAI_BASE_URL": "http://mock-endpoint:8000/v1",
            "ARCGEN_MODEL": "test-model-v1",
            "ARCGEN_EMBED_MODEL": "test-embed-v1",
        }
        with patch.dict(os.environ, mock_env):
            gen = ArcTaskGenerator(root=Path(self.temp_dir))
            # Mock subprocess.run to verify passed environment
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stderr="test failure", stdout="")
                # Mock upstream script existence
                (gen.upstream_root).mkdir(parents=True, exist_ok=True)
                (gen.upstream_root / "generate_tasks.py").write_text("# dummy")
                try:
                    gen._run_upstream(1, "standard")
                except RuntimeError:
                    pass
                self.assertTrue(mock_run.called)
                called_env = mock_run.call_args[1]["env"]
                self.assertEqual(called_env.get("OPENAI_BASE_URL"), "http://mock-endpoint:8000/v1")
                self.assertEqual(called_env.get("ARCGEN_MODEL"), "test-model-v1")
                self.assertEqual(called_env.get("ARCGEN_EMBED_MODEL"), "test-embed-v1")

    def test_subprocess_failure_clean_error_and_no_credential_leak(self):
        """D & J: Subprocess failure raises RuntimeError and redacts keys from error messages."""
        secret_key = "sk-secret-abcdef123456789"
        with patch.dict(os.environ, {"OPENAI_API_KEY": secret_key}):
            gen = ArcTaskGenerator(root=Path(self.temp_dir))
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stderr=f"Error connecting to API using key {secret_key}: Unauthorized",
                    stdout="",
                )
                (gen.upstream_root).mkdir(parents=True, exist_ok=True)
                (gen.upstream_root / "generate_tasks.py").write_text("# dummy")
                with self.assertRaises(RuntimeError) as ctx:
                    gen._run_upstream(1, "standard")
                err_msg = str(ctx.exception)
                self.assertNotIn(secret_key, err_msg)
                self.assertIn("[REDACTED_API_KEY]", err_msg)

    def test_malformed_generator_output(self):
        """E: Malformed tasks.json produces clear ValueError."""
        gen = ArcTaskGenerator(root=Path(self.temp_dir))
        upstream_gen_dir = gen.upstream_root / "data" / "generations" / "gen_20260101_120000"
        upstream_gen_dir.mkdir(parents=True, exist_ok=True)
        (upstream_gen_dir / "tasks.json").write_text("NOT_VALID_JSON{")
        (gen.upstream_root / "generate_tasks.py").write_text("# dummy")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
            with self.assertRaises(ValueError) as ctx:
                gen._run_upstream(1, "standard")
            self.assertIn("malformed JSON", str(ctx.exception))

    def test_missing_generation_directory(self):
        """F: Missing upstream generation directory produces FileNotFoundError."""
        gen = ArcTaskGenerator(root=Path(self.temp_dir))
        gen.upstream_root.mkdir(parents=True, exist_ok=True)
        (gen.upstream_root / "generate_tasks.py").write_text("# dummy")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
            with self.assertRaises(FileNotFoundError) as ctx:
                gen._run_upstream(1, "standard")
            self.assertIn("No generation artifacts were created", str(ctx.exception))

    def test_successful_artifact_synchronization(self):
        """G & H: Generated artifacts are cleanly synced into data/generations/<run_id>/."""
        gen = ArcTaskGenerator(root=Path(self.temp_dir))
        upstream_run_dir = gen.upstream_root / "data" / "generations" / "gen_20260905_120000"
        upstream_run_dir.mkdir(parents=True, exist_ok=True)
        sample_tasks = {
            "task_001": {
                "train": [{"input": [[1, 0], [0, 1]], "output": [[0, 1], [1, 0]]}],
                "test": [{"input": [[2, 0], [0, 2]], "output": [[0, 2], [2, 0]]}],
            }
        }
        (upstream_run_dir / "tasks.json").write_text(json.dumps(sample_tasks))
        (upstream_run_dir / "sanity_check.json").write_text(json.dumps({"overall": "PASS"}))
        (gen.upstream_root / "generate_tasks.py").write_text("# dummy")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
            tasks = gen._run_upstream(1, "standard")
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0]["train"][0]["input"], [[1, 0], [0, 1]])

            synced_dir = gen.generations_dir / "gen_20260905_120000"
            self.assertTrue(synced_dir.exists())
            self.assertTrue((synced_dir / "tasks.json").exists())
            self.assertTrue((synced_dir / "sanity_check.json").exists())

    def test_api_generate_single_and_multi(self):
        """K & L: POST /api/tasks/generate returns opaque IDs, hidden outputs, and mode."""
        # Single task
        resp1 = self.client.post("/api/tasks/generate", json={"count": 1, "mode": "standard"})
        self.assertEqual(resp1.status_code, 200, resp1.text)
        data1 = resp1.json()
        self.assertEqual(data1["task_id"], "FRESH-001")
        self.assertIn("train", data1)
        self.assertIn("test", data1)
        for pair in data1["test"]:
            self.assertNotIn("output", pair)
            self.assertIn("input", pair)
        self.assertIn("generator_mode", data1)
        self.assertIn("warning", data1)

        # Multi-task
        resp2 = self.client.post("/api/tasks/generate", json={"count": 3, "mode": "standard"})
        self.assertEqual(resp2.status_code, 200, resp2.text)
        data2 = resp2.json()
        self.assertEqual(data2["task_count"], 3)
        self.assertEqual(len(data2["tasks"]), 3)
        for i, t in enumerate(data2["tasks"], start=1):
            self.assertEqual(t["task_id"], f"FRESH-{i:03d}")
            for pair in t["test"]:
                self.assertNotIn("output", pair)


    def test_end_to_end_generation_to_loader_and_experiment(self):
        """M: Verify the full pipeline: generate -> disk storage -> load_generated_tasks -> experiment consumption."""
        # 1. Generate tasks using the adapter
        tasks = self.generator.generate(2, mode="standard")
        self.assertEqual(len(tasks), 2)
        run_id = self.generator.run_id
        self.assertIsNotNone(run_id)

        # 2. Check disk storage under data/generations/<run_id>/tasks.json
        tasks_file = self.generator.generations_dir / run_id / "tasks.json"
        self.assertTrue(tasks_file.exists())

        # 3. Verify arc_engine.load_generated_tasks loads these tasks
        with patch("backend.arc_engine.GENERATIONS_DIR", self.generator.generations_dir):
            loaded_by_id = load_generated_tasks(run_id)
            self.assertEqual(len(loaded_by_id), 2)
            self.assertIn("FRESH-001", loaded_by_id)

            loaded_latest = load_generated_tasks(None)
            self.assertEqual(len(loaded_latest), 2)
            self.assertIn("FRESH-001", loaded_latest)

        # 4. Verify experiment execution consumes generated tasks through the pipeline
        resp = self.client.post(
            "/api/experiments/run",
            json={"public_limit": 2, "fresh_count": 2, "solver": "heuristic", "mode": "standard"},
        )
        self.assertEqual(resp.status_code, 200, resp.text)
        exp_data = resp.json()
        self.assertIn("experiment_id", exp_data)
        self.assertEqual(exp_data["fresh"]["task_count"], 2)
        self.assertIn("accuracy", exp_data["fresh"])
        self.assertIn("gap", exp_data)
        self.assertIn("generator", exp_data)
        self.assertEqual(exp_data["generator"]["task_count"], 2)
        self.assertIn("distribution", exp_data)
        self.assertIn("fresh", exp_data["distribution"])


if __name__ == "__main__":
    unittest.main()
