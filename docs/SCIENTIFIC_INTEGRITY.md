# Scientific Integrity

## Central Claim

> **"High performance on a public benchmark does not by itself establish generalization to novel tasks. A public-vs-fresh, distribution-matched comparison provides diagnostic evidence about a possible generalization gap, but does not prove memorization."**

The project explicitly avoids hard claims of memorization from a performance gap alone. A performance gap between public benchmark tasks and fresh distribution-matched tasks is a **diagnostic signal**, not definitive causal proof of training-set contamination or memorization.

## Confounding Explanations

Any measured gap between public and fresh evaluation sets is consistent with multiple confounding factors:

1. **Benchmark familiarity**: The evaluated model may have encountered public tasks or recurring patterns during pretraining.
2. **Distribution mismatch**: Despite matching summary statistics, generated tasks may differ in higher-order combinatorial complexity or structural motifs.
3. **Generator artifacts**: Tasks generated via LLMs may exhibit idiosyncratic biases, unnatural symmetry requirements, or semantic artifacts.
4. **Task ambiguity**: Generated demonstrations may support multiple valid, competing rule interpretations under human cognitive priors.
5. **Difficulty shift**: The sampled fresh tasks may inherently possess higher or lower Kolmogorov complexity.
6. **Solver limitations**: Heuristic or neural baseline solvers may fit the inductive biases of public tasks better than newly created distributions.

## Statistical Honesty & Exploratory Caveats

- For sample sizes $N < 50$, results are strictly presented as exploratory, and statistical uncertainty is substantial.
- We explicitly do not fabricate unwarranted confidence intervals or hypothesis tests when sample sizes are statistically insufficient.
- Fallback runs are clearly labeled as **FALLBACK / DEMONSTRATION** and never presented as evidence from the upstream live generator.
