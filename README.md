# ARC Generalization Lab

**Does an AI benchmark measure generalization—or familiarity?**

🌐 **Live Public Web Demonstration:** [ARC Generalization Lab — Does benchmark performance survive fresh tasks?](https://famous-sable-446bd6.netlify.app/)  
📦 **Public Source Code Repository:** [Astha167/ARC_Generalization_Lab](https://github.com/Astha167/ARC_Generalization_Lab)

An interactive research laboratory that investigates whether AI performance on the public ARC-AGI-1 evaluation set generalizes to freshly generated, distribution-matched ARC-style tasks.

## Research Question

> If we take the same solver and evaluate it on both public ARC tasks (which may appear in training data) and fresh tasks (which cannot), does the performance change? And if so, what does the gap actually tell us?

## Central Claim

Performance measured on public ARC-AGI-1 evaluation tasks can differ from performance on newly generated, distribution-matched ARC-style tasks. This gap provides a **diagnostic signal** about how much benchmark familiarity may contribute to measured few-shot rule-induction performance.

**A performance gap does NOT prove memorization.** Possible explanations include benchmark familiarity, distribution mismatch, generator artifacts, task ambiguity, and solver limitations.

## Intended Audience & Prerequisites

**Audience:** Data scientists, ML engineers, and AI researchers interested in benchmark evaluation integrity, test-time adaptation, and abstract reasoning. Also suitable for advanced undergraduates in machine learning courses exploring generalization vs. memorization.

**Prerequisites:**
- Understanding of neural network training fundamentals (forward pass, backward pass, gradient-based optimization)
- Basic linear algebra (matrix multiplication, norms)
- Familiarity with benchmark evaluation concepts (train/test splits, accuracy metrics, data leakage)
- No prior knowledge of ARC-AGI or BDH-CQ is required — the artifact teaches both

## Learning Objectives

After completing the guided experience, the learner will be able to:

1. **Explain** why high accuracy on a public benchmark does not, by itself, prove generalization to novel tasks.
2. **Distinguish** benchmark familiarity (performance inflated by prior exposure) from genuine few-shot rule induction.
3. **Design** a diagnostic comparison between public and freshly generated, distribution-matched evaluation tasks to detect a possible generalization gap.
4. **Interpret** a public-vs-fresh performance gap as a diagnostic signal consistent with multiple competing hypotheses — not as conclusive proof of memorization.
5. **Contrast** optimization-based test-time adaptation (gradient updates on test instances) with BDH-CQ's forward-pass recurrent state accumulation (zero parameter updates at inference time).

## Architecture

```
frontend/          Vite + vanilla JS — interactive ARC grid, experiment lab
backend/           FastAPI — task serving, solver execution, evaluation
arc-task-gen/      Upstream generator (pathwaycom/arc-task-gen, MIT)
data/demo/         Hand-crafted demo tasks (clearly labeled DEMO DATA)
data/generations/  Private generated tasks (.gitignored)
docs/              Research documentation
experiments/       Experiment configs and results
```

## Quick Start

### Demo Mode (no API key required)

```bash
# Frontend only — works offline with embedded demo data
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### With Backend

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Live Generation (requires OpenAI-compatible API)

```bash
cp .env.example .env
# Edit .env with your API credentials
# Then start backend — live generation will be available
```

## Three Data Modes

| Mode | Label | Source | API Required |
|------|-------|--------|-------------|
| DEMO | `DEMO DATA — NOT AN EXPERIMENTAL RESULT` | Hand-crafted examples | No |
| PUBLIC | `PUBLIC DATA` | ARC-AGI-1 evaluation set (400 tasks) | Backend only |
| GENERATED | `LIVE GENERATED TASK` | arc-task-gen pipeline | Yes |

## How Fresh Tasks Are Generated

The [pathwaycom/arc-task-gen](https://github.com/pathwaycom/arc-task-gen) pipeline:

1. **Distribution Analysis** — Measure public ARC-AGI-1 evaluation set properties
2. **Joint Constraint Sampling** — Sample from a real eval task to preserve covariance
3. **LLM Task Generation** — Generate a new transformation rule matching constraints
4. **Structural Validation** — Verify valid grids, cell values 0–9, pair counts
5. **Semantic Deduplication** — Remove generated tasks too similar to each other
6. **Public-Eval Similarity Filter** — Remove tasks too close to official eval tasks

**Important:** Solvability is not programmatically verified. Generated tasks pass structural validation but may have ambiguous rules. This is a known limitation.

## arc-task-gen Integration

The upstream repository is included as a dependency at `arc-task-gen/`. The backend wraps it through the FastAPI adapter rather than duplicating its logic. Attribution and MIT license are preserved.

## Public vs Fresh Methodology

1. Select a solver (heuristic baseline, random baseline, or optional LLM)
2. Evaluate on a sample of public ARC-AGI-1 tasks
3. Evaluate on the same number of fresh generated tasks
4. Compute the performance gap
5. Analyze failures by task properties
6. Interpret with appropriate caution

### Statistical Methods

- **Exact-match accuracy**: Binary per-task success rate
- **Cell accuracy**: Proportion of correct cells (finer-grained)
- **Generalization gap**: Difference in accuracy between public and fresh sets

For small sample sizes, results should be interpreted as exploratory, not definitive.

## 60-Second Guided Learner Journey

For a rapid, self-contained walkthrough of the central claim, the lab features a 5-step guided experience:
1. **Try Task**: Infer an ARC transformation from a minimal input $\to$ output demonstration, inspect heuristic solver execution, and reveal reference ground truth.
2. **Core Question**: Reason about whether high public benchmark accuracy proves general rule induction (Answer: No, public accuracy alone cannot distinguish generalization from prior familiarity).
3. **Diagnostic Test**: Trigger a live comparison between public ARC-AGI-1 evaluation tasks and fresh, distribution-matched generated tasks using the exact same solver.
4. **Interpret the Gap**: Learn why a performance gap is diagnostic evidence consistent with 5 competing explanations (familiarity, distribution mismatch, generator artifacts, task ambiguity, solver baseline limitations) rather than conclusive proof of memorization.
5. **Adaptation Bridge**: Discover how BDH-CQ accumulates task demonstrations at evaluation time into an evolving recurrent associative state without test-time backpropagation or parameter updates ($\nabla_W \mathcal{L} = 0$).

## BDH-CQ Connection & Evidence Discipline

BDH-CQ (a 150M-parameter recurrent reasoning model) reports **29.5% pass@2** on public ARC-AGI-1 at **$0.0007 per task** without evaluation-time parameter tuning.
- **Published Results**: Developer-reported figures cited from Engdahl et al. (2026) and Pathway technical documentation. They are clearly labeled as `PUBLISHED RESULT — PATHWAY` and are not independently re-trained here.
- **Toy Recurrent Sandbox**: An in-browser $4 \times 4$ associative state simulation demonstrating non-parametric demonstration binding. Explicitly badged as an `Educational toy model inspired by the published BDH-CQ mechanism — NOT the official BDH-CQ implementation`.

## Scientific Literature Inventory (2022–2026)

The project grounds its claims in three recent qualifying primary papers and foundational literature:

1. **Engdahl et al. (2026)** — *BDH-CQ: Introducing In-Context Learning with Recurrent Latent Reasoning* (arXiv:2608.09888).
   - *Supported Claim*: In-context learning via recurrent associative latent memory without test-time parameter updates ($\nabla_W \mathcal{L} = 0$).
2. **Bordes et al. (2024)** — *An In-Depth Look at Gemini's ARC-AGI Capabilities and Contamination* (arXiv:2407.00645).
   - *Supported Claim*: Web crawl contamination inflates public ARC benchmarks, requiring freshly generated task sets for diagnostic isolation.
3. **Akyürek, Damani, Qiu, Guo, Kim, & Andreas (2024)** — *The Surprising Effectiveness of Test-Time Training for Abstract Reasoning* (arXiv:2411.07279).
   - *Supported Claim*: Demonstrates gradient-based test-time training (TTT) on ARC, serving as the empirical benchmark of optimization-based parameter adaptation that contrasts with BDH-CQ's forward-pass recurrent state accumulation.
4. *Foundational Reference*: **Chollet (2019)** — *On the Measure of Intelligence* (arXiv:1911.01547).

## Data and Evidence Taxonomy

Every piece of data and numerical result in the application is strictly labeled:
- `PUBLISHED RESULT — PATHWAY`: Cited from literature/repositories.
- `MEASURED FRESH-GENERATION EVIDENCE`: When live upstream `arc-task-gen` execution is run with configured credentials.
- `FALLBACK / DEMONSTRATION`: When local test-safe tasks are used (never disguised as genuine live generation).
- `DEMO DATA`: Hand-crafted tutorial tasks (`DEMO-001` through `DEMO-003`).
- `TOY / DIDACTIC`: Browser-computed educational recurrence.

## Limitations

- Generated task solvability is not programmatically guaranteed (addressed partially via blind human audit).
- Distribution matching covers measurable properties only (grid size, color count, pair counts).
- Generator artifacts may introduce systematic biases into fresh tasks.
- Small sample sizes ($N < 50$) yield exploratory diagnostic signals, not definitive conclusions.
- The performance gap has multiple possible causes — memorization is only one possibility.
- Fresh tasks are described as *"freshly generated for this evaluation run"*, never as *"guaranteed unseen"*.

## Reproducibility

Every experiment records: seed, timestamp, model, solver, configuration, thresholds, task count. Private generated tasks are not committed to version control (following upstream methodology).

To run all verified automated tests:
```bash
python -m unittest discover -s backend/tests
```

## License

- This project: MIT
- arc-task-gen: MIT ([pathwaycom/arc-task-gen](https://github.com/pathwaycom/arc-task-gen))
- ARC-AGI data: Apache 2.0 ([fchollet/ARC-AGI](https://github.com/fchollet/ARC-AGI))

## Provenance

See [docs/provenance.md](docs/provenance.md) for full source/license inventory and qualifying literature.

## AI Disclosure

See [docs/ai-disclosure.md](docs/ai-disclosure.md). AI tools assisted with coding, research, and documentation. All claims are verified against primary sources.
