"""ARC Generalization Lab — Backend API

FastAPI server providing:
- Public ARC-AGI-1 task access
- Demo task serving
- Baseline solver execution
- Prediction evaluation
- Distribution statistics and comparison
- arc-task-gen adapter for live generation

All generated task answers are withheld until after prediction submission.
Private metadata (rule descriptions, slot provenance) is never exposed.
"""

import json
import os
import random
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from arc_engine import (
        load_public_tasks,
        load_demo_tasks,
        load_generated_tasks,
        validate_task,
        evaluate_prediction,
        compute_stats,
        compare_distributions,
        ARC_COLORS,
    )
    from arc_generator import ArcTaskGenerator
    from solvers import get_solver, SOLVERS
except ModuleNotFoundError:  # pragma: no cover - supports repo-root imports
    from backend.arc_engine import (
        load_public_tasks,
        load_demo_tasks,
        load_generated_tasks,
        validate_task,
        evaluate_prediction,
        compute_stats,
        compare_distributions,
        ARC_COLORS,
    )
    from backend.arc_generator import ArcTaskGenerator
    from backend.solvers import get_solver, SOLVERS

load_dotenv()

app = FastAPI(
    title="ARC Generalization Lab API",
    description="Backend for the ARC Generalization Lab — investigating benchmark generalization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory caches
# ---------------------------------------------------------------------------

_public_tasks: Optional[dict] = None
_demo_tasks: Optional[dict] = None


def get_public_tasks() -> dict:
    global _public_tasks
    if _public_tasks is None:
        _public_tasks = load_public_tasks()
    return _public_tasks


def get_demo_tasks() -> dict:
    global _demo_tasks
    if _demo_tasks is None:
        _demo_tasks = load_demo_tasks()
    return _demo_tasks


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------

class PredictionRequest(BaseModel):
    task_id: str
    dataset: str  # "public", "demo", "generated"
    predicted: list[list[int]]


class SolverRequest(BaseModel):
    task_id: str
    dataset: str
    solver: str = "heuristic"


class BatchEvalRequest(BaseModel):
    dataset: str
    solver: str = "heuristic"
    task_ids: Optional[list[str]] = None
    max_tasks: int = 20


class GenerateTaskRequest(BaseModel):
    count: int = 1
    n: Optional[int] = None
    mode: str = "standard"


class ExperimentRequest(BaseModel):
    public_limit: int = 10
    fresh_count: int = 5
    solver: str = "heuristic"
    mode: str = "standard"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    return {
        "status": "ok",
        "mode": "live" if has_api_key else "demo",
        "generator_available": has_api_key,
        "public_tasks_loaded": _public_tasks is not None,
    }


# ---------------------------------------------------------------------------
# Task endpoints
# ---------------------------------------------------------------------------

@app.get("/api/tasks/public")
def list_public_tasks(limit: int = 20, offset: int = 0):
    """List public ARC-AGI-1 tasks (IDs + metadata, no answers)."""
    tasks = get_public_tasks()
    ids = sorted(tasks.keys())[offset : offset + limit]
    result = []
    for tid in ids:
        task = tasks[tid]
        result.append({
            "id": tid,
            "dataset": "public",
            "label": "PUBLIC DATA",
            "train_pairs": len(task["train"]),
            "test_pairs": len(task["test"]),
            "input_shape": [
                len(task["train"][0]["input"]),
                len(task["train"][0]["input"][0]) if task["train"][0]["input"] else 0,
            ],
        })
    return {"tasks": result, "total": len(tasks)}


@app.get("/api/tasks/public/{task_id}")
def get_public_task(task_id: str):
    """Get a public task: train examples + test input. Test output is withheld."""
    tasks = get_public_tasks()
    if task_id not in tasks:
        raise HTTPException(404, f"Task {task_id} not found")
    task = tasks[task_id]
    return {
        "id": task_id,
        "dataset": "public",
        "label": "PUBLIC DATA",
        "train": task["train"],
        "test": [{"input": t["input"]} for t in task["test"]],
    }


@app.get("/api/tasks/demo")
def list_demo_tasks():
    """List demo tasks (hand-crafted, clearly labeled)."""
    tasks = get_demo_tasks()
    result = []
    for tid, task in sorted(tasks.items()):
        result.append({
            "id": tid,
            "dataset": "demo",
            "label": "DEMO DATA — NOT AN EXPERIMENTAL RESULT",
            "train_pairs": len(task.get("train", [])),
            "test_pairs": len(task.get("test", [])),
        })
    return {"tasks": result, "total": len(tasks)}


@app.get("/api/tasks/demo/{task_id}")
def get_demo_task(task_id: str):
    """Get a demo task: train + test input. Test output withheld until evaluation."""
    tasks = get_demo_tasks()
    if task_id not in tasks:
        raise HTTPException(404, f"Demo task {task_id} not found")
    task = tasks[task_id]
    return {
        "id": task_id,
        "dataset": "demo",
        "label": "DEMO DATA — NOT AN EXPERIMENTAL RESULT",
        "train": task["train"],
        "test": [{"input": t["input"]} for t in task["test"]],
    }
@app.get("/api/tasks/generated")
def list_generated_tasks_endpoint(run_id: Optional[str] = None):
    """List generated tasks without test outputs, properly labeled with generation mode."""
    tasks = load_generated_tasks(run_id=run_id)
    result = []
    for tid, task in sorted(tasks.items()):
        result.append({
            "id": tid,
            "dataset": "generated",
            "label": "FRESH GENERATED TASK",
            "train_pairs": len(task.get("train", [])),
            "test_pairs": len(task.get("test", [])),
        })
    return {"tasks": result, "total": len(tasks), "run_id": run_id}


@app.get("/api/tasks/generated/{task_id}")
def get_generated_task(task_id: str, run_id: Optional[str] = None):
    """Get a generated task: train pairs + test inputs only. Test outputs are strictly withheld."""
    tasks = load_generated_tasks(run_id=run_id)
    if task_id not in tasks:
        raise HTTPException(404, f"Generated task {task_id} not found")
    task = tasks[task_id]
    return {
        "id": task_id,
        "dataset": "generated",
        "label": "FRESH GENERATED TASK",
        "train": task.get("train", []),
        "test": [{"input": t["input"]} for t in task.get("test", [])],
    }


@app.get("/api/audit/tasks")
def get_audit_tasks():
    """Get tasks for the blind solvability audit.
    Protocol:
    - If live generated tasks exist from an upstream run, use LIVE GENERATED TASKS.
    - If only fallback or demo tasks exist, use DEMO DATA with an explicit demonstration disclaimer.
    - The evaluator must NEVER see test outputs, private rules, or generation metadata.
    """
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    generated_tasks = load_generated_tasks()

    # Determine whether we have live generated tasks
    source = "demo"
    label = "BLIND AUDIT — DEMO DATA (Demonstration Only)"
    disclaimer = "Currently evaluating hand-crafted demo tasks. This audit demonstrates the human evaluation protocol but does not validate the live generator."
    tasks_to_serve = {}

    if generated_tasks and has_api_key:
        source = "live_generated"
        label = "BLIND AUDIT — LIVE GENERATED TASKS"
        disclaimer = "Evaluating fresh tasks produced by the upstream arc-task-gen pipeline."
        tasks_to_serve = generated_tasks
    elif generated_tasks:
        source = "fallback_generated"
        label = "BLIND AUDIT — FALLBACK GENERATED TASKS"
        disclaimer = "Evaluating deterministic fallback generated tasks (offline mode)."
        tasks_to_serve = generated_tasks
    else:
        tasks_to_serve = get_demo_tasks()

    sanitized_tasks = []
    for tid, task in sorted(tasks_to_serve.items()):
        # Exclude test outputs and all private metadata
        sanitized_tasks.append({
            "id": tid,
            "train": task.get("train", []),
            "test": [{"input": t["input"]} for t in task.get("test", [])],
        })

    return {
        "source": source,
        "label": label,
        "disclaimer": disclaimer,
        "total": len(sanitized_tasks),
        "tasks": sanitized_tasks,
    }

@app.post("/api/tasks/generate")
def generate_tasks(req: GenerateTaskRequest):
    """Generate a fresh ARC-style task using the upstream arc-task-gen pipeline.

    The API intentionally returns only public-facing task content: train examples
    and test-input grids. Private rule metadata, provenance, embedding scores,
    similarity flags, and answer keys remain hidden.
    """
    target_count = req.count if req.count and req.count > 0 else (req.n or 1)
    if target_count < 1:
        raise HTTPException(400, "count must be >= 1")
    if req.mode not in {"standard", "stratified"}:
        raise HTTPException(400, "mode must be 'standard' or 'stratified'")

    generator = ArcTaskGenerator()
    try:
        if req.mode == "stratified":
            tasks = generator.generate_stratified(target_count)
        else:
            tasks = generator.generate(target_count, mode="standard")
    except Exception as exc:
        raise HTTPException(500, f"Task generation failed: {exc}") from exc

    if not tasks:
        raise HTTPException(500, "Generation produced no tasks")

    public_tasks = []
    for idx, task in enumerate(tasks, start=1):
        errors = validate_task(task)
        if errors:
            raise HTTPException(500, f"Generated task failed validation: {errors}")
        test_inputs = [{"input": pair["input"]} for pair in task["test"]]
        public_tasks.append({
            "task_id": f"FRESH-{idx:03d}",
            "train": task["train"],
            "test": test_inputs,
            "status": "generated",
        })

    warning = None if generator.generator_mode == "live" else "No OpenAI-compatible generator credentials were configured; returned deterministic fallback tasks instead of a live arc-task-gen run."

    if len(public_tasks) == 1:
        payload = dict(public_tasks[0])
        payload["run_id"] = generator.run_id
        payload["generated_by"] = "arc-task-gen"
        payload["generation_time_seconds"] = generator.execution_time_seconds
        payload["generator_mode"] = generator.generator_mode
        if warning:
            payload["warning"] = warning
        return payload

    return {
        "run_id": generator.run_id,
        "status": "completed",
        "task_count": len(public_tasks),
        "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "generation_time_seconds": generator.execution_time_seconds,
        "generator_mode": generator.generator_mode,
        "tasks": public_tasks,
        **({"warning": warning} if warning else {}),
    }


@app.post("/api/experiments/run")
def run_experiment(req: ExperimentRequest):
    """Run a small public-vs-fresh evaluation using the same solver configuration."""
    public_tasks = get_public_tasks()
    if not public_tasks:
        raise HTTPException(404, "No public ARC-AGI-1 tasks loaded")

    public_ids = sorted(public_tasks.keys())[: max(1, req.public_limit)]
    public_subset = {task_id: public_tasks[task_id] for task_id in public_ids}

    generator = ArcTaskGenerator()
    try:
        fresh_tasks_raw = generator.generate(max(1, req.fresh_count), mode=req.mode)
    except Exception as exc:
        raise HTTPException(500, f"Fresh generation failed: {exc}") from exc
    fresh_task_map = {}
    for idx, task in enumerate(fresh_tasks_raw, start=1):
        if validate_task(task):
            continue
        fresh_task_map[f"FRESH-{idx:03d}"] = task
    if not fresh_task_map:
        raise HTTPException(500, "Fresh generation produced no valid tasks")

    if req.solver not in SOLVERS:
        raise HTTPException(400, f"Unknown solver: {req.solver}. Available: {list(SOLVERS.keys())}")
    solver = get_solver(req.solver)
    public_results = []
    for task_id, task in public_subset.items():
        pred = solver.solve(task)
        gt = task["test"][0]["output"]
        evaluation = evaluate_prediction(pred, gt)
        public_results.append({
            "task_id": task_id,
            "exact_match": evaluation["exact_match"],
            "cell_accuracy": evaluation["cell_accuracy"],
            "solver": req.solver,
        })

    fresh_results = []
    for task_id, task in list(fresh_task_map.items())[: max(1, req.fresh_count)]:
        pred = solver.solve(task)
        gt = task["test"][0]["output"]
        evaluation = evaluate_prediction(pred, gt)
        fresh_results.append({
            "task_id": task_id,
            "exact_match": evaluation["exact_match"],
            "cell_accuracy": evaluation["cell_accuracy"],
            "solver": req.solver,
        })

    public_solved = sum(1 for r in public_results if r["exact_match"])
    fresh_solved = sum(1 for r in fresh_results if r["exact_match"])
    public_acc = sum(r["cell_accuracy"] for r in public_results) / max(1, len(public_results))
    fresh_acc = sum(r["cell_accuracy"] for r in fresh_results) / max(1, len(fresh_results))
    gap = public_acc - fresh_acc

    is_genuine_experiment = (generator.generator_mode == "live")
    if is_genuine_experiment:
        generator_warning = None
        evidence_label = "MEASURED FRESH-GENERATION EVIDENCE"
    else:
        generator_warning = (
            "No OpenAI-compatible generator credentials were configured; this experiment used the deterministic "
            "fallback generation path. This result MUST NOT be presented as a genuine public-vs-fresh generation "
            "experiment because fresh tasks were not produced by the upstream arc-task-gen generator in this run."
        )
        evidence_label = "FALLBACK / DEMONSTRATION"

    exploratory_warning = (
        "Small sample size (N < 50): result is exploratory and uncertainty is substantial. "
        "Performance gap cannot isolate memorization from confounding factors (distribution shift, difficulty, solver limits)."
        if (len(public_results) < 50 or len(fresh_results) < 50) else None
    )

    experiment = {
        "experiment_id": f"exp-{__import__('time').time_ns()}",
        "evidence_label": evidence_label,
        "public_dataset": "ARC-AGI-1 evaluation",
        "public_data_source": "official_evaluation_set",
        "fresh_dataset": "arc-task-gen" if is_genuine_experiment else "fallback-local",
        "fresh_data_source": "upstream_arc_task_gen" if is_genuine_experiment else "deterministic_fallback",
        "generator_mode": generator.generator_mode,
        "genuine_experiment": is_genuine_experiment,
        "metric_definition": "gap = public_accuracy - fresh_accuracy (mean cell accuracy difference)",
        "gap_interpretation": "Diagnostic performance gap (not proof of memorization; consistent with distribution shift, difficulty variance, generator artifacts, task ambiguity, or solver bias)",
        "exploratory_warning": exploratory_warning,
        "solver": {
            "name": req.solver,
            "type": "heuristic",
            "parameters": {},
            "seed": None,
        },
        "public": {
            "dataset_name": "ARC-AGI-1 evaluation",
            "dataset_source": "official_evaluation_set",
            "total_benchmark_tasks": len(public_tasks),
            "task_count": len(public_results),
            "evaluated_tasks_label": f"PUBLIC TASKS EVALUATED: {len(public_results)} (of {len(public_tasks)} total)",
            "solved": public_solved,
            "accuracy": round(public_acc, 4),
            "solver": req.solver,
        },
        "fresh": {
            "dataset_name": "arc-task-gen" if is_genuine_experiment else "fallback-local",
            "dataset_source": "upstream_arc_task_gen" if is_genuine_experiment else "deterministic_fallback",
            "task_count": len(fresh_results),
            "evaluated_tasks_label": f"FRESH TASKS EVALUATED: {len(fresh_results)}",
            "solved": fresh_solved,
            "accuracy": round(fresh_acc, 4),
            "solver": req.solver,
            "generator_mode": generator.generator_mode,
        },
        "gap": round(gap, 4),
        "distribution": {
            "public": compute_stats(public_subset),
            "fresh": compute_stats(fresh_task_map),
        },
        "generator": {
            "run_id": generator.run_id,
            "status": "completed" if generator.run_id else "failed",
            "task_count": len(fresh_task_map),
            "generation_time_seconds": generator.execution_time_seconds,
            "mode": generator.generator_mode,
        },
        **({"warning": generator_warning} if generator_warning else {}),
    }

    results_dir = Path(__file__).resolve().parent.parent / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / f"{experiment['experiment_id']}.json"
    out_path.write_text(__import__("json").dumps(experiment, indent=2))
    return experiment


@app.get("/api/experiments")
def list_experiments():
    """List all saved experiment runs."""
    results_dir = Path(__file__).resolve().parent.parent / "experiments" / "results"
    if not results_dir.exists():
        return {"experiments": []}
    files = sorted(results_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    experiments = []
    for f in files:
        try:
            data = json.loads(f.read_text())
            experiments.append({
                "experiment_id": data.get("experiment_id", f.stem),
                "public_dataset": data.get("public_dataset"),
                "fresh_dataset": data.get("fresh_dataset"),
                "generator_mode": data.get("generator_mode", data.get("generator", {}).get("mode", "unknown")),
                "genuine_experiment": data.get("genuine_experiment", False),
                "public_accuracy": data.get("public", {}).get("accuracy"),
                "fresh_accuracy": data.get("fresh", {}).get("accuracy"),
                "gap": data.get("gap"),
                "solver": data.get("solver", {}).get("name"),
            })
        except Exception:
            continue
    return {"experiments": experiments, "total": len(experiments)}


@app.get("/api/experiments/{experiment_id}")
def get_experiment(experiment_id: str):
    """Retrieve full details of a saved experiment run."""
    results_dir = Path(__file__).resolve().parent.parent / "experiments" / "results"
    target = results_dir / f"{experiment_id}.json"
    if not target.exists():
        raise HTTPException(404, f"Experiment {experiment_id} not found")
    try:
        return json.loads(target.read_text())
    except Exception as exc:
        raise HTTPException(500, f"Failed to load experiment {experiment_id}: {exc}") from exc


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

@app.post("/api/evaluate")
def evaluate(req: PredictionRequest):
    """Evaluate a prediction against ground truth. Reveals the answer."""
    if req.dataset == "public":
        tasks = get_public_tasks()
    elif req.dataset == "demo":
        tasks = get_demo_tasks()
    elif req.dataset == "generated":
        tasks = load_generated_tasks()
    else:
        raise HTTPException(400, f"Unknown dataset: {req.dataset}")

    if req.task_id not in tasks:
        raise HTTPException(404, f"Task {req.task_id} not found in {req.dataset}")

    task = tasks[req.task_id]
    ground_truth = task["test"][0]["output"]

    result = evaluate_prediction(req.predicted, ground_truth)
    result["ground_truth"] = ground_truth
    result["task_id"] = req.task_id
    result["dataset"] = req.dataset
    return result


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

@app.get("/api/solvers")
def list_solvers():
    """List available solvers."""
    return {
        "solvers": [
            get_solver(name).metadata()
            for name in SOLVERS
        ]
    }


@app.post("/api/solver/run")
def run_solver(req: SolverRequest):
    """Run a solver on a task and return prediction + evaluation."""
    if req.dataset == "public":
        tasks = get_public_tasks()
    elif req.dataset == "demo":
        tasks = get_demo_tasks()
    elif req.dataset == "generated":
        tasks = load_generated_tasks()
    else:
        raise HTTPException(400, f"Unknown dataset: {req.dataset}")

    if req.task_id not in tasks:
        raise HTTPException(404, f"Task {req.task_id} not found")

    task = tasks[req.task_id]
    solver = get_solver(req.solver)

    t0 = time.time()
    predicted = solver.solve(task)
    elapsed = time.time() - t0

    ground_truth = task["test"][0]["output"]
    eval_result = evaluate_prediction(predicted, ground_truth)

    return {
        "task_id": req.task_id,
        "dataset": req.dataset,
        "solver": solver.metadata(),
        "predicted": predicted,
        "ground_truth": ground_truth,
        "evaluation": eval_result,
        "elapsed_ms": round(elapsed * 1000, 1),
    }


@app.post("/api/solver/batch")
def batch_evaluate(req: BatchEvalRequest):
    """Run a solver on multiple tasks. Returns aggregate statistics."""
    if req.dataset == "public":
        tasks = get_public_tasks()
    elif req.dataset == "demo":
        tasks = get_demo_tasks()
    elif req.dataset == "generated":
        tasks = load_generated_tasks()
    else:
        raise HTTPException(400, f"Unknown dataset: {req.dataset}")

    if not tasks:
        raise HTTPException(404, f"No tasks found in {req.dataset}")

    task_ids = req.task_ids or sorted(tasks.keys())
    task_ids = task_ids[: req.max_tasks]

    solver = get_solver(req.solver)
    results = []
    solved = 0
    total_accuracy = 0.0

    for tid in task_ids:
        if tid not in tasks:
            continue
        task = tasks[tid]
        t0 = time.time()
        predicted = solver.solve(task)
        elapsed = time.time() - t0
        ground_truth = task["test"][0]["output"]
        evaluation = evaluate_prediction(predicted, ground_truth)
        if evaluation["exact_match"]:
            solved += 1
        total_accuracy += evaluation["cell_accuracy"]
        results.append({
            "task_id": tid,
            "exact_match": evaluation["exact_match"],
            "cell_accuracy": evaluation["cell_accuracy"],
            "elapsed_ms": round(elapsed * 1000, 1),
        })

    n = len(results)
    return {
        "dataset": req.dataset,
        "label": "MEASURED" if req.dataset != "demo" else "DEMO DATA",
        "solver": solver.metadata(),
        "total_tasks": n,
        "solved": solved,
        "accuracy": round(solved / n, 4) if n > 0 else 0,
        "mean_cell_accuracy": round(total_accuracy / n, 4) if n > 0 else 0,
        "results": results,
    }


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

@app.get("/api/stats/distribution")
def distribution_stats(dataset: str = "public"):
    """Compute distribution statistics for a dataset."""
    if dataset == "public":
        tasks = get_public_tasks()
        label = "PUBLIC DATA"
    elif dataset == "demo":
        tasks = get_demo_tasks()
        label = "DEMO DATA"
    elif dataset == "generated":
        tasks = load_generated_tasks()
        label = "GENERATED DATA"
    else:
        raise HTTPException(400, f"Unknown dataset: {dataset}")

    stats = compute_stats(tasks)
    # Remove raw value arrays from response (too large for API)
    for key in list(stats.keys()):
        if isinstance(stats[key], dict) and "values" in stats[key]:
            stats[key] = {k: v for k, v in stats[key].items() if k != "values"}

    return {"dataset": dataset, "label": label, "stats": stats}


@app.get("/api/stats/compare")
def compare_stats(dataset_a: str = "public", dataset_b: str = "generated"):
    """Compare distribution statistics between two datasets."""
    loaders = {
        "public": get_public_tasks,
        "demo": get_demo_tasks,
        "generated": load_generated_tasks,
    }
    if dataset_a not in loaders or dataset_b not in loaders:
        raise HTTPException(400, "Invalid dataset name")

    tasks_a = loaders[dataset_a]()
    tasks_b = loaders[dataset_b]()

    if not tasks_a:
        raise HTTPException(404, f"No tasks in {dataset_a}")
    if not tasks_b:
        raise HTTPException(404, f"No tasks in {dataset_b}")

    stats_a = compute_stats(tasks_a)
    stats_b = compute_stats(tasks_b)
    comparison = compare_distributions(stats_a, stats_b)

    return {
        "datasets": [dataset_a, dataset_b],
        "comparison": comparison,
        "stats": {
            dataset_a: {k: {kk: vv for kk, vv in v.items() if kk != "values"}
                        if isinstance(v, dict) else v
                        for k, v in stats_a.items()},
            dataset_b: {k: {kk: vv for kk, vv in v.items() if kk != "values"}
                        if isinstance(v, dict) else v
                        for k, v in stats_b.items()},
        },
    }


@app.get("/api/colors")
def arc_colors():
    """Return the ARC color palette."""
    return ARC_COLORS
