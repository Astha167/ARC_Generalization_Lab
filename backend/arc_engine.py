"""ARC Engine — Core task management, validation, evaluation, and statistics.

Handles loading public ARC-AGI-1 tasks, demo tasks, generated tasks,
evaluating predictions against ground truth, and computing distribution statistics.
"""

import io
import json
import math
import statistics
import tarfile
from collections import Counter
from pathlib import Path
from typing import Optional

import httpx

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEMO_DIR = DATA_DIR / "demo"
EVAL_PATH = DATA_DIR / "arc_agi_eval.json"
GENERATIONS_DIR = DATA_DIR / "generations"

DATASET_TARBALL = "https://codeload.github.com/fchollet/ARC-AGI/tar.gz/refs/heads/master"
DATASET_PREFIX = "ARC-AGI-master/data/evaluation/"

# ARC color palette (matches official ARC-AGI colors)
ARC_COLORS = {
    0: "#000000",  # black (background)
    1: "#0074D9",  # blue
    2: "#FF4136",  # red
    3: "#2ECC40",  # green
    4: "#FFDC00",  # yellow
    5: "#AAAAAA",  # grey
    6: "#F012BE",  # magenta
    7: "#FF851B",  # orange
    8: "#7FDBFF",  # azure
    9: "#870C25",  # maroon
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_public_tasks() -> dict:
    """Load the 400-task ARC-AGI-1 evaluation set, downloading on first use."""
    if EVAL_PATH.exists():
        return json.loads(EVAL_PATH.read_text())

    print(f"Downloading ARC-AGI-1 evaluation set -> {EVAL_PATH} ...")
    resp = httpx.get(DATASET_TARBALL, timeout=300, follow_redirects=True)
    resp.raise_for_status()

    tasks = {}
    with tarfile.open(fileobj=io.BytesIO(resp.content), mode="r:gz") as tar:
        for member in tar.getmembers():
            if (member.isfile()
                    and member.name.startswith(DATASET_PREFIX)
                    and member.name.endswith(".json")):
                tasks[Path(member.name).stem] = json.loads(
                    tar.extractfile(member).read()
                )

    EVAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_PATH.write_text(json.dumps(tasks))
    print(f"Cached {len(tasks)} evaluation tasks.")
    return tasks


def load_demo_tasks() -> dict:
    """Load hand-crafted demo tasks from data/demo/."""
    tasks = {}
    if DEMO_DIR.exists():
        for f in sorted(DEMO_DIR.glob("*.json")):
            data = json.loads(f.read_text())
            tasks[f.stem] = data
    return tasks


def load_generated_tasks(run_id: Optional[str] = None) -> dict:
    """Load tasks from a generation run. If run_id is None, load the latest."""
    if not GENERATIONS_DIR.exists():
        return {}
    if run_id:
        tasks_path = GENERATIONS_DIR / run_id / "tasks.json"
    else:
        runs = [p for p in GENERATIONS_DIR.iterdir() if p.is_dir()]
        if not runs:
            return {}
        latest_run = max(runs, key=lambda p: (p.stat().st_mtime, p.name))
        tasks_path = latest_run / "tasks.json"
    if not tasks_path.exists():
        return {}
    return json.loads(tasks_path.read_text())


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_task(task: dict) -> list[str]:
    """Validate a single ARC task. Returns list of error strings (empty = valid)."""
    errors = []
    if "train" not in task or "test" not in task:
        return ["missing 'train' or 'test' key"]
    if len(task["train"]) < 2:
        errors.append("fewer than 2 training pairs")
    for split in ("train", "test"):
        for i, pair in enumerate(task[split]):
            for field in ("input", "output"):
                grid = pair.get(field)
                if not isinstance(grid, list) or not all(
                    isinstance(row, list) for row in grid
                ):
                    errors.append(f"{split}[{i}].{field}: not a 2-D list")
                    continue
                if len(grid) == 0:
                    errors.append(f"{split}[{i}].{field}: empty grid")
                    continue
                col_lens = {len(row) for row in grid}
                if len(col_lens) != 1:
                    errors.append(f"{split}[{i}].{field}: ragged rows")
                for row in grid:
                    for cell in row:
                        if not isinstance(cell, int) or cell < 0 or cell > 9:
                            errors.append(
                                f"{split}[{i}].{field}: cell {cell!r} out of range 0-9"
                            )
    return errors


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_prediction(
    predicted: list[list[int]], ground_truth: list[list[int]]
) -> dict:
    """Compare a predicted grid against ground truth. Returns detailed evaluation."""
    exact_match = predicted == ground_truth

    pred_rows = len(predicted)
    pred_cols = len(predicted[0]) if predicted else 0
    gt_rows = len(ground_truth)
    gt_cols = len(ground_truth[0]) if ground_truth else 0

    dimensions_match = pred_rows == gt_rows and pred_cols == gt_cols

    diff = []
    correct_cells = 0
    total_cells = 0

    if dimensions_match:
        for r in range(gt_rows):
            diff_row = []
            for c in range(gt_cols):
                match = predicted[r][c] == ground_truth[r][c]
                if match:
                    correct_cells += 1
                total_cells += 1
                diff_row.append({
                    "predicted": predicted[r][c],
                    "expected": ground_truth[r][c],
                    "match": match,
                })
            diff.append(diff_row)
    else:
        total_cells = gt_rows * gt_cols

    cell_accuracy = correct_cells / total_cells if total_cells > 0 else 0.0

    return {
        "exact_match": exact_match,
        "dimensions_match": dimensions_match,
        "cell_accuracy": round(cell_accuracy, 4),
        "correct_cells": correct_cells,
        "total_cells": total_cells,
        "predicted_shape": [pred_rows, pred_cols],
        "expected_shape": [gt_rows, gt_cols],
        "diff": diff if dimensions_match else None,
    }


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def compute_stats(tasks: dict) -> dict:
    """Compute distribution statistics for a set of ARC tasks.

    Mirrors the upstream arc-task-gen compute_stats() logic so that
    the numbers are directly comparable.
    """
    train_counts, test_counts = [], []
    in_rows, in_cols, in_areas = [], [], []
    out_areas = []
    colors_per_task = []

    for task in tasks.values():
        train_counts.append(len(task.get("train", [])))
        test_counts.append(len(task.get("test", [])))
        task_colors = set()
        for split in ("train", "test"):
            for pair in task.get(split, []):
                for field in ("input", "output"):
                    grid = pair.get(field)
                    if not grid:
                        continue
                    r = len(grid)
                    c = len(grid[0]) if grid[0] else 0
                    if field == "input":
                        in_rows.append(r)
                        in_cols.append(c)
                        in_areas.append(r * c)
                    else:
                        out_areas.append(r * c)
                    for row in grid:
                        task_colors.update(v for v in row if v != 0)
        colors_per_task.append(len(task_colors))

    def summarise(lst):
        if not lst:
            return {}
        return {
            "min": min(lst),
            "max": max(lst),
            "mean": round(statistics.mean(lst), 2),
            "median": statistics.median(lst),
            "stdev": round(statistics.stdev(lst), 2) if len(lst) > 1 else 0.0,
            "values": lst,  # raw values for frontend distribution plotting
        }

    return {
        "num_tasks": len(tasks),
        "train_pairs_per_task": dict(sorted(Counter(train_counts).items())),
        "test_pairs_per_task": dict(sorted(Counter(test_counts).items())),
        "input_rows": summarise(in_rows),
        "input_cols": summarise(in_cols),
        "input_area": summarise(in_areas),
        "output_area": summarise(out_areas),
        "colors_per_task": summarise(colors_per_task),
    }


def compare_distributions(stats_a: dict, stats_b: dict) -> dict:
    """Compare two sets of ARC task statistics."""
    comparisons = {}
    for metric in ("input_area", "input_rows", "input_cols", "colors_per_task"):
        a = stats_a.get(metric, {})
        b = stats_b.get(metric, {})
        if not a or not b:
            continue
        comparisons[metric] = {
            "public": {k: v for k, v in a.items() if k != "values"},
            "fresh": {k: v for k, v in b.items() if k != "values"},
            "mean_diff": round(abs(a.get("mean", 0) - b.get("mean", 0)), 2),
            "median_diff": round(abs(a.get("median", 0) - b.get("median", 0)), 2),
        }
    return comparisons
