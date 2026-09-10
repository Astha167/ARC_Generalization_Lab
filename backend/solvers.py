"""Pluggable ARC solvers — from naive baselines to optional LLM solvers.

Every solver implements the same interface so that the evaluation
pipeline can swap solvers without code changes.

IMPORTANT: These are LIGHTWEIGHT HEURISTIC BASELINES, not competitive
ARC solvers. They exist to demonstrate the evaluation methodology,
not to achieve high accuracy.
"""

import random
from abc import ABC, abstractmethod
from typing import Optional


class Solver(ABC):
    """Base interface for ARC task solvers."""

    @abstractmethod
    def solve(self, task: dict) -> list[list[int]]:
        """Given a task dict with 'train' and 'test', predict the first test output."""
        ...

    @abstractmethod
    def metadata(self) -> dict:
        """Return solver metadata: name, type, description."""
        ...


class RandomSolver(Solver):
    """Produces a random grid matching the test input dimensions.

    This is a DELIBERATELY WEAK baseline. Its purpose is to establish
    a performance floor — any meaningful solver should substantially
    exceed random performance.
    """

    def __init__(self, seed: int | None = None):
        self.seed = seed

    def solve(self, task: dict) -> list[list[int]]:
        test_input = task["test"][0]["input"]
        rows = len(test_input)
        cols = len(test_input[0]) if test_input else 0

        # Collect colors used in training
        colors = set()
        for pair in task["train"]:
            for field in ("input", "output"):
                for row in pair[field]:
                    colors.update(row)
        color_list = list(colors) if colors else [0]

        rng = random.Random(self.seed) if self.seed is not None else random
        return [[rng.choice(color_list) for _ in range(cols)] for _ in range(rows)]

    def metadata(self) -> dict:
        return {
            "name": "Random Baseline",
            "type": "random",
            "description": (
                "Generates a random grid using colors from the training examples. "
                "Deliberately weak — establishes the performance floor."
            ),
        }


# ---------------------------------------------------------------------------
# Heuristic helpers — colour remapping, tiling, border, flood-fill
# ---------------------------------------------------------------------------

def _build_color_map(inp: list[list[int]], out: list[list[int]]) -> dict[int, int] | None:
    """Derive a colour remapping from a single input→output pair.

    Returns a dict mapping every input colour to its output colour,
    or None if the grids differ in shape or if colours map inconsistently.
    """
    if len(inp) != len(out):
        return None
    mapping: dict[int, int] = {}
    for r in range(len(inp)):
        if len(inp[r]) != len(out[r]):
            return None
        for c in range(len(inp[r])):
            src, dst = inp[r][c], out[r][c]
            if src in mapping:
                if mapping[src] != dst:
                    return None
            else:
                mapping[src] = dst
    return mapping


def _apply_color_map(grid: list[list[int]], mapping: dict[int, int]) -> list[list[int]]:
    """Apply a colour remapping to a grid."""
    return [[mapping.get(v, v) for v in row] for row in grid]


def _try_tile(inp: list[list[int]], out: list[list[int]]) -> tuple[int, int] | None:
    """Check whether *out* is *inp* tiled kR × kC times (integer multiples)."""
    ir, ic = len(inp), len(inp[0]) if inp else 0
    orr, oc = len(out), len(out[0]) if out else 0
    if ir == 0 or ic == 0 or orr == 0 or oc == 0:
        return None
    if orr % ir != 0 or oc % ic != 0:
        return None
    kr, kc = orr // ir, oc // ic
    if kr == 1 and kc == 1:
        return None  # identity, handled separately
    for r in range(orr):
        for c in range(oc):
            if out[r][c] != inp[r % ir][c % ic]:
                return None
    return (kr, kc)


def _apply_tile(grid: list[list[int]], kr: int, kc: int) -> list[list[int]]:
    """Tile *grid* kr × kc times."""
    rows, cols = len(grid), len(grid[0]) if grid else 0
    return [[grid[r % rows][c % cols] for c in range(cols * kc)] for r in range(rows * kr)]


def _extract_border(grid: list[list[int]]) -> list[list[int]]:
    """Keep only the border cells, filling interior with 0."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    if rows <= 2 or cols <= 2:
        return [row[:] for row in grid]
    result = []
    for r in range(rows):
        new_row = []
        for c in range(cols):
            if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                new_row.append(grid[r][c])
            else:
                new_row.append(0)
        result.append(new_row)
    return result


def _fill_from_nonzero(grid: list[list[int]]) -> list[list[int]]:
    """For grids with exactly one non-zero colour, flood its row and column
    to form a cross pattern (common in simple ARC tasks)."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    colors = set()
    positions = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                colors.add(grid[r][c])
                positions.append((r, c))
    if len(colors) != 1 or len(positions) != 1:
        return None  # not applicable
    color = list(colors)[0]
    pr, pc = positions[0]
    result = [row[:] for row in grid]
    for r in range(rows):
        result[r][pc] = color
    for c in range(cols):
        result[pr][c] = color
    return result


def _gravity_down(grid: list[list[int]]) -> list[list[int]]:
    """Drop all non-zero cells to the bottom of each column (gravity)."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    result = [[0] * cols for _ in range(rows)]
    for c in range(cols):
        vals = [grid[r][c] for r in range(rows) if grid[r][c] != 0]
        start = rows - len(vals)
        for i, v in enumerate(vals):
            result[start + i][c] = v
    return result


def _gravity_left(grid: list[list[int]]) -> list[list[int]]:
    """Compact all non-zero cells to the left of each row."""
    result = []
    for row in grid:
        vals = [v for v in row if v != 0]
        new_row = vals + [0] * (len(row) - len(vals))
        result.append(new_row)
    return result


def _upscale_2x(grid: list[list[int]]) -> list[list[int]]:
    """Scale each cell to a 2×2 block."""
    result = []
    for row in grid:
        new_row = []
        for v in row:
            new_row.extend([v, v])
        result.append(new_row[:])
        result.append(new_row[:])
    return result


class HeuristicSolver(Solver):
    """Attempts ARC transformations: geometric, colour remap, tiling, borders, gravity.

    Tests each heuristic against training pairs and uses the first one
    that produces correct outputs. Falls back to identity (copy input).

    This is a LIGHTWEIGHT HEURISTIC BASELINE, not a competitive solver.
    It covers common ARC transformation families to produce meaningful
    diagnostic results while remaining transparent and auditable.
    """

    def solve(self, task: dict) -> list[list[int]]:
        test_input = task["test"][0]["input"]
        train = task["train"]

        # --- Phase 1: simple geometric transforms ---
        for name, transform in self._geometric_transforms():
            if self._check_transform(train, transform):
                return transform(test_input)

        # --- Phase 2: colour remapping ---
        color_pred = self._try_color_remap(train, test_input)
        if color_pred is not None:
            return color_pred

        # --- Phase 3: tiling ---
        tile_pred = self._try_tiling(train, test_input)
        if tile_pred is not None:
            return tile_pred

        # --- Phase 4: structural transforms (border, fill, gravity, upscale) ---
        for name, transform in self._structural_transforms():
            if self._check_transform(train, transform):
                return transform(test_input)

        # --- Phase 5: combined geometric + colour remap ---
        combined_pred = self._try_combined_geo_color(train, test_input)
        if combined_pred is not None:
            return combined_pred

        # Fallback: copy input
        return [row[:] for row in test_input]

    # ---- Geometric transforms ----

    def _geometric_transforms(self):
        """Yield (name, transform_fn) pairs for pure geometric transforms."""
        yield "identity", lambda g: [row[:] for row in g]
        yield "h_flip", lambda g: [row[::-1] for row in g]
        yield "v_flip", lambda g: list(reversed([row[:] for row in g]))
        yield "rotate_90", self._rotate_90
        yield "rotate_180", lambda g: list(reversed([row[::-1] for row in g]))
        yield "rotate_270", self._rotate_270
        yield "transpose", self._transpose

    # ---- Structural transforms ----

    def _structural_transforms(self):
        """Yield (name, transform_fn) for structural heuristics."""
        yield "border_extract", _extract_border
        yield "gravity_down", _gravity_down
        yield "gravity_left", _gravity_left
        yield "upscale_2x", _upscale_2x
        yield "fill_cross", lambda g: _fill_from_nonzero(g) if _fill_from_nonzero(g) is not None else [row[:] for row in g]

    # ---- Colour remapping ----

    def _try_color_remap(self, train, test_input):
        """Try to learn a consistent colour mapping from all training pairs."""
        global_map: dict[int, int] = {}
        for pair in train:
            m = _build_color_map(pair["input"], pair["output"])
            if m is None:
                return None
            for src, dst in m.items():
                if src in global_map:
                    if global_map[src] != dst:
                        return None
                else:
                    global_map[src] = dst
        # Verify on all training pairs
        for pair in train:
            result = _apply_color_map(pair["input"], global_map)
            if result != pair["output"]:
                return None
        # Non-zero colours in test_input must be covered by global_map
        test_colors = {v for row in test_input for v in row if v != 0}
        if not test_colors.issubset(set(global_map.keys())):
            return None
        return _apply_color_map(test_input, global_map)

    # ---- Tiling ----

    def _try_tiling(self, train, test_input):
        """Try to learn a consistent tile factor from all training pairs."""
        tile_factors = set()
        for pair in train:
            factor = _try_tile(pair["input"], pair["output"])
            if factor is None:
                return None
            tile_factors.add(factor)
        if len(tile_factors) != 1:
            return None
        kr, kc = tile_factors.pop()
        # Verify on all
        for pair in train:
            if _apply_tile(pair["input"], kr, kc) != pair["output"]:
                return None
        return _apply_tile(test_input, kr, kc)

    # ---- Combined geometric + colour remap ----

    def _try_combined_geo_color(self, train, test_input):
        """Try applying a geometric transform followed by a colour remap."""
        for geo_name, geo_fn in self._geometric_transforms():
            if geo_name == "identity":
                continue  # pure colour remap already handled
            # Build colour map after geometric transform
            global_map: dict[int, int] = {}
            valid = True
            for pair in train:
                try:
                    transformed = geo_fn(pair["input"])
                except (IndexError, TypeError):
                    valid = False
                    break
                m = _build_color_map(transformed, pair["output"])
                if m is None:
                    valid = False
                    break
                for src, dst in m.items():
                    if src in global_map:
                        if global_map[src] != dst:
                            valid = False
                            break
                    else:
                        global_map[src] = dst
                if not valid:
                    break
            if not valid:
                continue
            # Verify on all training pairs
            all_match = True
            for pair in train:
                try:
                    if _apply_color_map(geo_fn(pair["input"]), global_map) != pair["output"]:
                        all_match = False
                        break
                except (IndexError, TypeError):
                    all_match = False
                    break
            if all_match:
                try:
                    trans_test = geo_fn(test_input)
                    test_colors = {v for row in trans_test for v in row if v != 0}
                    if test_colors.issubset(set(global_map.keys())):
                        return _apply_color_map(trans_test, global_map)
                except (IndexError, TypeError):
                    continue
        return None

    @staticmethod
    def _rotate_90(grid):
        rows, cols = len(grid), len(grid[0]) if grid else 0
        return [[grid[rows - 1 - r][c] for r in range(rows)] for c in range(cols)]

    @staticmethod
    def _rotate_270(grid):
        rows, cols = len(grid), len(grid[0]) if grid else 0
        return [[grid[r][cols - 1 - c] for r in range(rows)] for c in range(cols)]

    @staticmethod
    def _transpose(grid):
        rows, cols = len(grid), len(grid[0]) if grid else 0
        return [[grid[r][c] for r in range(rows)] for c in range(cols)]

    @staticmethod
    def _check_transform(train_pairs, transform) -> bool:
        """Check if transform produces correct output for ALL training pairs."""
        for pair in train_pairs:
            inp = pair["input"]
            expected = pair["output"]
            try:
                result = transform(inp)
                if result != expected:
                    return False
            except (IndexError, TypeError, AttributeError):
                return False
        return True

    def metadata(self) -> dict:
        return {
            "name": "Heuristic Baseline",
            "type": "heuristic",
            "description": (
                "Tests geometric transforms (flip, rotate, transpose), colour remapping, "
                "tiling, border extraction, gravity, cross-fill, 2× upscale, and combined "
                "geo+colour pipelines against training pairs. Falls back to copying the "
                "input. Covers common ARC transformation families but remains lightweight."
            ),
        }


# Registry of available solvers
SOLVERS = {
    "random": RandomSolver,
    "heuristic": HeuristicSolver,
}


def get_solver(name: str) -> Solver:
    """Get a solver instance by name."""
    cls = SOLVERS.get(name)
    if cls is None:
        raise ValueError(f"Unknown solver: {name}. Available: {list(SOLVERS.keys())}")
    return cls()
