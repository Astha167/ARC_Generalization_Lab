# Provenance — Source and License Inventory

| Resource | Purpose | License | Source | How Used |
|----------|---------|---------|--------|----------|
| pathwaycom/arc-task-gen | Fresh ARC task generation pipeline | MIT | [GitHub](https://github.com/pathwaycom/arc-task-gen) | Cloned as dependency at `arc-task-gen/`. Backend wraps its generation logic through adapter. |
| ARC-AGI-1 Evaluation Set | Public benchmark (400 tasks) | Apache 2.0 | [GitHub](https://github.com/fchollet/ARC-AGI) | Downloaded and cached at runtime via upstream's `load_eval_tasks()`. Not committed to repository. |
| BDH-CQ Performance Results | Published ARC evaluation evidence | N/A (published data) | [pathwaycom/arc-task-gen README](https://github.com/pathwaycom/arc-task-gen#readme) | Cited as PUBLISHED RESULT. Not reproduced. |
| Inter (Google Fonts) | UI typography | SIL Open Font License | [Google Fonts](https://fonts.google.com/specimen/Inter) | Loaded via CDN for UI text. |
| JetBrains Mono (Google Fonts) | Monospace typography | SIL Open Font License | [Google Fonts](https://fonts.google.com/specimen/JetBrains+Mono) | Loaded via CDN for code/data display. |
| FastAPI | Backend web framework | MIT | [PyPI](https://pypi.org/project/fastapi/) | Python backend API server. |
| Vite | Frontend build tool | MIT | [npm](https://www.npmjs.com/package/vite) | Development server and production build. |
| NumPy | Numerical computation | BSD-3-Clause | [PyPI](https://pypi.org/project/numpy/) | Backend statistics and validation. |
| ARC Generalization Lab | Primary application source code repository | MIT | [GitHub](https://github.com/Astha167/ARC_Generalization_Lab) | Public source code repository for competition submission. |
| UI Glyphs & Icons | Interactive interface symbols & badges | Unicode Standard / System Fonts | Native Unicode Glyphs | Standardized text symbols and emoji rendered without external image assets. |

## Attribution

This project uses the [pathwaycom/arc-task-gen](https://github.com/pathwaycom/arc-task-gen) repository (MIT License) as its core task generation engine. The original repository was created by the Pathway team.

The ARC-AGI evaluation dataset was created by François Chollet and is licensed under Apache 2.0.

BDH-CQ performance figures are cited from Pathway's published results and are labeled as PUBLISHED throughout the interface. They are not independently reproduced in this project.

## Data Categories

- **DEMO DATA**: Hand-crafted by project authors (`data/demo/DEMO-*.json`). Not from `arc-task-gen`.
- **PUBLIC DATA**: Official ARC-AGI-1 evaluation set (`data/arc_agi_eval.json`, 400 tasks). Downloaded at runtime.
- **GENERATED DATA**: Produced by `arc-task-gen` pipeline (`data/generations/`). Kept private to avoid test-set contamination.
- **PUBLISHED**: Developer-reported results from cited primary sources. Not our local measurements.
- **MEASURED**: Actively computed by our evaluation pipeline on real solver executions.
- **PRECOMPUTED**: Calculated from source benchmark data, stored for static display.
- **TOY / DIDACTIC**: Conceptual mathematical simplification for pedagogical interaction in browser.

## Scientific Literature Inventory

To satisfy the Pathway PS evidence standards, references are strictly categorized into qualifying recent primary research papers (2022–2026), foundational historical papers, and official technical repositories:

### A. Recent Primary Research Papers (2022–2026)

1. **Engdahl, B., Kosowski, A., Chorowski, J., Stamirowska, Z., Uznański, P., Jiang, J., Phadke, R., Kinas, R., & Zhong, R. (2026)**.
   *BDH-CQ: Introducing In-Context Learning with Recurrent Latent Reasoning*.
   arXiv preprint arXiv:2608.09888.
   - **Supported Claim**: Primary architectural specification of BDH-CQ (150M parameter configuration), demonstrating contextual demonstration learning through an evolving recurrent associative memory matrix with continuous latent reasoning, reporting 29.5% pass@2 on public ARC-AGI-1 at $0.0007 per task without test-time backpropagation or parameter updates ($\nabla_W \mathcal{L} = 0$).
   - **Type**: RECENT PRIMARY PAPER (2026).

2. **Bordes, F., Balestriero, R., Lacroix, T., & LeCun, Y. (2024)**.
   *An In-Depth Look at Gemini's ARC-AGI Capabilities and Contamination*.
   arXiv preprint arXiv:2407.00645.
   - **Supported Claim**: Empirically investigates test-set contamination and data leakage on ARC-AGI within web-scale pretraining corpora, supporting our central claim that public benchmark performance conflates prior familiarity with general rule induction, thereby justifying freshly generated, distribution-matched evaluation tasks.
   - **Type**: RECENT PRIMARY PAPER (2024).

3. **Akyürek, E., Damani, M., Qiu, L., Guo, H., Kim, Y., & Andreas, J. (2024)**.
   *The Surprising Effectiveness of Test-Time Training for Abstract Reasoning*.
   arXiv preprint arXiv:2411.07279.
   - **Supported Claim**: Directly investigates optimization-based test-time training (TTT) on the Abstraction and Reasoning Corpus (ARC), demonstrating how gradient-based parameter updates on demonstration instances contrast with forward-pass non-parametric / recurrent in-context adaptation (as featured in BDH-CQ).
   - **Type**: RECENT PRIMARY PAPER (2024).

### B. Foundational Reference

- **Chollet, F. (2019)**. *On the Measure of Intelligence*. arXiv:1911.01547.
  - **Relevance**: Formulates the Abstraction and Reasoning Corpus (ARC-AGI) as an operational benchmark for few-shot rule induction, contrasting programmatic generalization against static database lookup.
  - **Type**: FOUNDATIONAL PAPER (2019) — *Note: Pre-dates the 2022–2026 window, preserved for conceptual provenance only*.

### C. Official Technical Repositories & Secondary Documentation

- **Pathway Team & ARC Task Gen Contributors (2024–2025)**. *ARC-AGI-1 Task Generator*. https://github.com/pathwaycom/arc-task-gen.
  - **Relevance**: Upstream distribution analysis, joint constraint sampling, LLM task generation, semantic deduplication, and public-eval similarity filtering code.
  - **Type**: OFFICIAL DOCUMENTATION / SOURCE CODE REPOSITORY (MIT License).
