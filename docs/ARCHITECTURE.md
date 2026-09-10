# Architecture

The project keeps the working Vite + vanilla JS frontend and FastAPI backend, and it layers in the official upstream `arc-task-gen` generator as a server-side dependency.

## Components

- `frontend/`: UI for ARC task inspection, comparison panels, and experiment controls.
- `backend/`: API layer, public dataset loader, solver execution, distribution stats, and generator orchestration.
- `arc-task-gen/`: upstream Pathway generator source of truth.
- `data/`: public ARC-AGI cache and generated run outputs.
- `experiments/results/`: persisted experiment JSON files.

## Data flow

1. The public ARC-AGI-1 evaluation set is downloaded once into `data/arc_agi_eval.json`.
2. The generator adapter invokes the upstream pipeline and stores a run under `data/generations/<run_id>/`.
3. The backend loads only public-safe task data for user-facing responses.
4. The same solver is applied to both public and fresh task sets during experiments.
5. Measurements are persisted under `experiments/results/` without committing private task payloads.

## Privacy

Generated tasks remain private by default. User-facing responses omit `test.output` and internal provenance. Answer keys are only used inside the backend evaluation path.
