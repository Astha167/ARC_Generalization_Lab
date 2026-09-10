# Experiment Methodology & Pipeline

## Central Claim

> **"High performance on a public benchmark does not by itself establish generalization to novel tasks. A public-vs-fresh, distribution-matched comparison provides diagnostic evidence about a possible generalization gap, but does not prove memorization."**

This lab measures public-vs-fresh performance using the exact same solver instance and scoring logic against two datasets:

- **Official Public ARC-AGI-1 evaluation set** (`data/arc_agi_eval.json`, 400 tasks)
- **Fresh Tasks** generated either by live upstream `arc-task-gen` execution or deterministic test-safe fallback (freshly generated for this evaluation run, not guaranteed unseen)

## Complete Execution Path

```text
POST /api/experiments/run
        ↓
Public ARC Dataset (ARC-AGI-1 evaluation set, subset of size N)
        ↓
Fresh Task Generation / Loading (ArcTaskGenerator adapter -> upstream arc-task-gen or fallback)
        ↓
Same Solver Abstraction (get_solver(req.solver) instance applied to both)
        ↓
Public Evaluation (predicted vs withheld ground truth -> exact_match, cell_accuracy)
        ↓
Fresh Evaluation (predicted vs withheld ground truth -> exact_match, cell_accuracy)
        ↓
Accuracy Calculation (mean cell accuracy and exact match counts per split)
        ↓
Generalization Gap (gap = public_accuracy - fresh_accuracy)
        ↓
Distribution Statistics (rows, cols, area, non-background colors, pair counts)
        ↓
Persisted Experiment Result (saved to experiments/results/exp-<id>.json without secrets)
```

## Data Regimes & Labeling

Every experiment run clearly distinguishes:
1. **LIVE GENERATION**: Upstream `arc-task-gen` execution using model credentials. Results tagged as `MEASURED FRESH-GENERATION EVIDENCE` with `genuine_experiment: true`.
2. **FALLBACK / DEMONSTRATION**: Deterministic locally generated ARC-compliant tasks used when credentials are not configured. Results tagged as `FALLBACK / DEMONSTRATION` with `genuine_experiment: false` and explicit disclaimers.
3. **DEMO DATA**: Hand-crafted educational tasks (`data/demo/DEMO-*.json`) strictly used for UI tutorials or demonstration audits.
4. **PRECOMPUTED**: Historical static runs stored on disk.
5. **MEASURED**: Actively computed by solver execution.

## Interpretation & Statistical Honesty

The metric is defined as:
$$\text{Performance Gap} = \text{Accuracy}_{\text{public}} - \text{Accuracy}_{\text{fresh}}$$

This is framed strictly as a **Diagnostic Performance Gap**, never as "memorization detected". The gap is consistent with multiple confounding explanations:
1. Benchmark familiarity
2. Distribution mismatch
3. Generator artifacts
4. Task ambiguity
5. Difficulty shift
6. Solver limitations

For $N < 50$, results are explicitly flagged as exploratory with substantial statistical uncertainty.
