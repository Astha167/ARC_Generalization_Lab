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

        return [[random.choice(color_list) for _ in range(cols)] for _ in range(rows)]

    def metadata(self) -> dict:
        return {
            "name": "Random Baseline",
            "type": "random",
            "description": (
                "Generates a random grid using colors from the training examples. "
                "Deliberately weak — establishes the performance floor."
            ),
        }


class HeuristicSolver(Solver):
    """Attempts basic ARC transformations: identity, flip, rotate, color mapping.

    Tests each heuristic against training pairs and uses the first one
    that produces correct outputs. Falls back to identity (copy input).

    This is a LIGHTWEIGHT HEURISTIC BASELINE, not a competitive solver.
    It can solve only the simplest ARC tasks.
    """

    def solve(self, task: dict) -> list[list[int]]:
        test_input = task["test"][0]["input"]
        train = task["train"]

        # Try each transformation on training data
        for name, transform in self._transforms():
            if self._check_transform(train, transform):
                return transform(test_input)

        # Fallback: copy input
        return [row[:] for row in test_input]

    def _transforms(self):
        """Yield (name, transform_fn) pairs."""
        yield "identity", lambda g: [row[:] for row in g]
        yield "h_flip", lambda g: [row[::-1] for row in g]
        yield "v_flip", lambda g: list(reversed([row[:] for row in g]))
        yield "rotate_90", self._rotate_90
        yield "rotate_180", lambda g: list(reversed([row[::-1] for row in g]))
        yield "rotate_270", self._rotate_270
        yield "transpose", self._transpose

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
            except (IndexError, TypeError):
                return False
        return True

    def metadata(self) -> dict:
        return {
            "name": "Heuristic Baseline",
            "type": "heuristic",
            "description": (
                "Tests simple geometric transforms (identity, flip, rotate, transpose) "
                "against training pairs and applies the first match. Falls back to "
                "copying the input. Can only solve the simplest ARC tasks."
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
