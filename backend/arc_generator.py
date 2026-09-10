"""Adapter around the upstream arc-task-gen generator.

This project ships the official generator under ../arc-task-gen. The backend
wraps it with a small abstraction that provides a clean Python API while keeping
an offline fallback for environments without an OpenAI-compatible API.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GENERATIONS_DIR = DATA_DIR / "generations"
UPSTREAM_ROOT = PROJECT_ROOT / "arc-task-gen"


class ArcTaskGenerator:
    """Thin adapter over the official arc-task-gen pipeline."""

    def __init__(self, root: Path | None = None):
        self.root = root or PROJECT_ROOT
        self.data_dir = self.root / "data"
        self.generations_dir = self.data_dir / "generations"
        self.upstream_root = self.root / "arc-task-gen"
        self.run_id: str | None = None
        self.last_error: str | None = None
        self.execution_time_seconds = 0.0
        self.generator_mode = "live" if self._has_live_generator() else "fallback"

    def _has_live_generator(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY")) and (self.upstream_root / "generate_tasks.py").exists()

    def _latest_generation_dir(self, base_dir: Path) -> Path | None:
        if not base_dir.exists():
            return None
        runs = [p for p in base_dir.iterdir() if p.is_dir()]
        if not runs:
            return None
        # Sort by mtime, breaking ties with directory name
        return max(runs, key=lambda p: (p.stat().st_mtime, p.name))

    def _sync_generated_artifacts(self, source_dir: Path) -> Path:
        self.generations_dir.mkdir(parents=True, exist_ok=True)
        dest_dir = self.generations_dir / source_dir.name
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        shutil.copytree(source_dir, dest_dir)
        return dest_dir

    def _redact_secrets(self, text: str) -> str:
        """Strip any API keys or tokens from text before returning or logging."""
        if not text:
            return text
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and len(api_key) > 6:
            text = text.replace(api_key, "[REDACTED_API_KEY]")
        # Redact generic sk- tokens
        import re
        text = re.sub(r"sk-[a-zA-Z0-9_-]{10,}", "[REDACTED_KEY]", text)
        return text

    def _run_upstream(self, n: int, mode: str) -> list[dict[str, Any]]:
        mode_name = "standard" if mode == "standard" else "stratified"
        script_name = "generate_tasks.py" if mode == "standard" else "generate_tasks_stratified.py"
        script_path = self.upstream_root / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Generator script not found: {script_path}")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.upstream_root) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        # Forward generator-specific environment variables if set
        for var in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "ARCGEN_MODEL", "ARCGEN_EMBED_MODEL"):
            val = os.environ.get(var)
            if val:
                env[var] = val

        start = __import__("time").perf_counter()
        command = [sys.executable, str(script_path), "--n", str(max(1, int(n)))]
        result = subprocess.run(
            command,
            cwd=str(self.upstream_root),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.execution_time_seconds = round(__import__("time").perf_counter() - start, 3)
        if result.returncode != 0:
            raw_err = result.stderr.strip() or result.stdout.strip() or f"Generator failed for mode={mode_name}"
            clean_err = self._redact_secrets(raw_err)
            raise RuntimeError(f"arc-task-gen execution failed (code {result.returncode}): {clean_err}")

        source_root = self.upstream_root / "data" / ("generations" if mode == "standard" else "generations_stratified")
        source_dir = self._latest_generation_dir(source_root)
        if source_dir is None:
            raise FileNotFoundError(f"No generation artifacts were created under {source_root}")

        synced_dir = self._sync_generated_artifacts(source_dir)
        self.run_id = synced_dir.name

        tasks_path = synced_dir / "tasks.json"
        if not tasks_path.exists():
            raise FileNotFoundError(f"Generated tasks file missing: {tasks_path}")
        try:
            tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        except Exception as err:
            raise ValueError(f"Generated tasks file is malformed JSON: {err}") from err

        return [tasks[task_id] for task_id in sorted(tasks)[:max(1, int(n))]]

    def _build_fallback_task(self, index: int) -> dict[str, Any]:
        templates = [
            {
                "train": [
                    {"input": [[0, 0, 0], [0, 1, 0], [0, 0, 0]], "output": [[0, 0, 0], [0, 1, 0], [0, 0, 0]]},
                    {"input": [[0, 0, 0], [0, 2, 0], [0, 0, 0]], "output": [[0, 0, 0], [0, 2, 0], [0, 0, 0]]},
                ],
                "test": [{"input": [[0, 0, 0], [0, 3, 0], [0, 0, 0]], "output": [[0, 0, 0], [0, 3, 0], [0, 0, 0]]}],
            },
            {
                "train": [
                    {"input": [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "output": [[0, 0, 0], [0, 0, 0], [0, 0, 1]]},
                    {"input": [[0, 0, 2], [0, 0, 0], [0, 0, 0]], "output": [[0, 0, 0], [0, 0, 0], [2, 0, 0]]},
                ],
                "test": [{"input": [[0, 0, 0], [0, 0, 0], [0, 0, 3]], "output": [[0, 0, 0], [0, 0, 0], [0, 0, 3]]}],
            },
            {
                "train": [
                    {"input": [[0, 0, 0], [0, 4, 0], [0, 0, 0]], "output": [[4, 4, 4], [4, 4, 4], [4, 4, 4]]},
                    {"input": [[0, 0, 0, 0], [0, 5, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], "output": [[5, 5, 5, 5], [5, 5, 5, 5], [5, 5, 5, 5], [5, 5, 5, 5]]},
                ],
                "test": [{"input": [[0, 0, 0], [0, 6, 0], [0, 0, 0]], "output": [[6, 6, 6], [6, 6, 6], [6, 6, 6]]}],
            },
        ]
        task = templates[index % len(templates)]
        # Make each fallback task structurally valid and deterministic.
        return {"train": task["train"], "test": task["test"]}

    def _fallback_generate(self, n: int, mode: str) -> list[dict[str, Any]]:
        start = __import__("time").perf_counter()
        tasks = [self._build_fallback_task(i) for i in range(max(1, int(n)))]
        run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.generations_dir / f"fallback_{run_ts}"
        run_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_dir.name
        self.execution_time_seconds = round(__import__("time").perf_counter() - start, 3)
        self.generator_mode = "fallback"
        payload = {f"FRESH-{i + 1:03d}": task for i, task in enumerate(tasks)}
        (run_dir / "tasks.json").write_text(json.dumps(payload))
        (run_dir / "sanity_check.json").write_text(json.dumps({"mode": mode, "fallback": True, "tasks": len(tasks), "generation_time_seconds": self.execution_time_seconds}))
        return tasks

    def generate_one(self) -> dict[str, Any]:
        tasks = self.generate(1, mode="standard")
        return tasks[0]

    def generate(self, n: int = 1, mode: str = "standard") -> list[dict[str, Any]]:
        mode = (mode or "standard").lower()
        if mode not in {"standard", "stratified"}:
            raise ValueError("mode must be 'standard' or 'stratified'")
        self.last_error = None
        try:
            if self._has_live_generator():
                self.generator_mode = "live"
                return self._run_upstream(max(1, int(n)), mode)
        except Exception as exc:  # pragma: no cover - fallback path is intentional.
            self.last_error = str(exc)
        self.generator_mode = "fallback"
        return self._fallback_generate(max(1, int(n)), mode)

    def generate_stratified(self, n: int = 1) -> list[dict[str, Any]]:
        return self.generate(n=n, mode="stratified")

    def validate(self, task: dict[str, Any] | None = None) -> list[str]:
        try:
            from arc_engine import validate_task
        except ModuleNotFoundError:  # pragma: no cover - supports repo-root imports
            from backend.arc_engine import validate_task

        if task is None:
            tasks = self._latest_tasks()
            if not tasks:
                return ["No generated tasks available"]
            errors = []
            for key, value in tasks.items():
                errors.extend([f"{key}: {err}" for err in validate_task(value)])
            return errors
        return validate_task(task)

    def _latest_tasks(self) -> dict[str, Any]:
        latest_dir = self._latest_generation_dir(self.generations_dir)
        if latest_dir is None:
            return {}
        tasks_path = latest_dir / "tasks.json"
        if not tasks_path.exists():
            return {}
        return json.loads(tasks_path.read_text())

    def get_generation_report(self) -> dict[str, Any]:
        latest_dir = self._latest_generation_dir(self.generations_dir)
        if latest_dir is None:
            return {"status": "no_generation", "error": self.last_error}
        sanity_path = latest_dir / "sanity_check.json"
        if sanity_path.exists():
            return json.loads(sanity_path.read_text())
        return {"status": "generated", "run_id": latest_dir.name, "tasks": self._latest_tasks()}


if __name__ == "__main__":
    generator = ArcTaskGenerator()
    tasks = generator.generate(1)
    print(json.dumps({"status": "ok", "count": len(tasks), "run_id": generator.run_id}))
