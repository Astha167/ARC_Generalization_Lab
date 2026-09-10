# Reproducibility Guide

## Automated Verification Tests

To run the full verified test suite:

```bash
cd c:/Users/astha/OneDrive/Documents/DataForge
python -m unittest discover -s backend/tests
```

*Note on test runner*: When `pytest` is not installed in the active environment, the standard library `unittest` discover runner is used.

## Starting the Backend

```bash
cd c:/Users/astha/OneDrive/Documents/DataForge/backend
uvicorn app:app --reload --port 8000
```

## Running Experiments & Queries

1. **Generate a Fresh Task (Privacy-Enforced)**:
```bash
curl -X POST http://localhost:8000/api/tasks/generate -H "Content-Type: application/json" -d "{\"count\":1,\"mode\":\"standard\"}"
```

2. **Run Public-vs-Fresh Experiment**:
```bash
curl -X POST http://localhost:8000/api/experiments/run -H "Content-Type: application/json" -d "{\"public_limit\":10,\"fresh_count\":5,\"solver\":\"heuristic\"}"
```

3. **Query Saved Experiment Runs**:
```bash
curl http://localhost:8000/api/experiments
```

4. **Blind Audit Tasks Endpoint**:
```bash
curl http://localhost:8000/api/audit/tasks
```

## Data Handling & Security

- `data/arc_agi_eval.json`: Official 400-task evaluation set cached locally.
- `data/generations/`: Generation runs synchronized from upstream or fallback.
- `experiments/results/`: Persisted experiment JSON files. Secrets and API keys are strictly redacted and excluded.
- Test outputs are withheld from all task-serving endpoints until submission.
