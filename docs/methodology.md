# Methodology

## 1. ARC-AGI-1

The Abstraction and Reasoning Corpus (ARC), created by François Chollet, tests few-shot rule induction: given a few input-output grid pairs demonstrating a transformation rule, infer the rule and apply it to a new input. The ARC-AGI-1 evaluation set contains 400 tasks, each with 2–5 training pairs and 1–2 test pairs. Grids are rectangular (1×1 to 30×30) with integer cell values 0–9.

## 2. The Central Claim

> **"High performance on a public benchmark does not by itself establish generalization to novel tasks. A public-vs-fresh, distribution-matched comparison provides diagnostic evidence about a possible generalization gap, but does not prove memorization."**

A performance gap does not uniquely identify memorization. Multiple alternative explanations are consistent with a public-to-fresh difference: benchmark familiarity, distribution mismatch in unmeasured cognitive dimensions, systematic biases or artifacts in the task generator, differences in task ambiguity, or solver baseline limitations.

## 3. Public Evaluation & Benchmark Familiarity

The standard evaluation protocol: present training pairs, receive a prediction for the test output, and compare against ground truth. Exact match (entire grid correct) is the primary metric.

The ARC-AGI-1 evaluation set has been publicly available since 2019. As demonstrated empirically by Bordes et al. (2024), public evaluation sets appear in web-scraped corpora (Common Crawl, The Pile, etc.) used to train large language models. A model evaluated on tasks it has seen during pretraining may score higher than its true generalization ability warrants. This is the benchmark familiarity problem.

## 4. Distribution Matching

To create a comparable but novel evaluation set, we generate tasks whose measurable properties match the public evaluation distribution. Matched properties include:
- Input grid dimensions (rows, columns)
- Number of distinct non-background colours
- Number of training pairs
- Number of test pairs

Properties are sampled jointly from single anchor tasks (joint constraint sampling) to preserve natural covariance — e.g., a 2×2 grid naturally has fewer colours than a 20×20 grid.

**Important distinction**: Generated tasks are matched to *selected measurable properties* of the public evaluation distribution. They are not guaranteed to match in all dimensions (cognitive complexity, visual salience, transformation type diversity).

## 5. Task Generation

The `pathwaycom/arc-task-gen` pipeline generates one task per LLM API call. The prompt specifies:
- Target grid dimensions
- Target colour count
- Number of training/test pairs
- An avoidance list of previously generated rules (for diversity)

The LLM invents a genuinely new transformation rule and produces the complete task (training pairs + test pair) in standard ARC JSON format.

## 6. Novelty Filtering

Generated tasks undergo two novelty filters:

**Semantic deduplication** (cosine threshold: 0.80): Rule descriptions of all generated tasks are embedded; pairs exceeding the threshold are flagged and the duplicate is regenerated.

**Public-eval similarity filter** (cosine threshold: 0.92): Generated task descriptions are compared against official eval task descriptions. Tasks exceeding the threshold are removed to prevent generating near-copies of public tasks.

Both filters run iteratively until convergence (no removals needed) or a stall limit is reached.

## 7. Structural Validation

Every generated task is validated:
- All grids are 2D lists of integers
- Cell values are in range 0–9
- No ragged rows
- At least 2 training pairs
- Both train and test keys present

Malformed tasks are removed and regenerated.

## 8. Blind Audit

Because solvability is not programmatically verified, a blind human audit assesses whether generated tasks have unambiguous, inferable rules. The evaluator sees only training examples (no rule description, no test output) and classifies each task as SOLVABLE, AMBIGUOUS, or INVALID.

## 9. Public vs Fresh Evaluation

The core experiment:
1. Select a solver (heuristic baseline, random baseline, or LLM)
2. Evaluate on N public ARC tasks
3. Evaluate on N fresh generated tasks
4. Compute the performance gap

All results are labeled with their data source: MEASURED for real computations, DEMO DATA for hand-crafted examples.

## 10. Statistical Interpretation

A performance gap is a diagnostic signal, not a conclusive finding. We explicitly present multiple possible explanations:
- **Benchmark familiarity**: The solver may perform better on familiar tasks
- **Distribution mismatch**: Fresh tasks may differ in unmeasured ways
- **Generator artifacts**: LLM-generated tasks may have systematic biases
- **Task ambiguity**: Some fresh tasks may have unclear rules
- **Difficulty shift**: Fresh tasks may be coincidentally harder or easier

For small sample sizes (N < 50), confidence intervals are wide and results should be treated as exploratory.

## 11. Limitations

- Solvability is not programmatically guaranteed
- Distribution matching is partial (measurable properties only)
- Generator artifacts may introduce systematic biases
- Sample sizes in demo mode are very small
- The performance gap cannot isolate a single cause
- Generated task IDs may leak transformation rules (we use opaque FRESH-NNN labels)
- Generated tasks are kept private to prevent contamination (following upstream methodology)
