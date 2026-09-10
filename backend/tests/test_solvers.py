"""Unit tests for ARC solvers including enhanced heuristic families.

Tests cover:
- Color remapping heuristics
- Tiling heuristics
- Structural transforms (border, gravity, upscale, fill)
- Combined geometric and color remapping
- HeuristicSolver end-to-end solving
- RandomSolver behavior
"""

import unittest
from backend.solvers import (
    HeuristicSolver,
    RandomSolver,
    get_solver,
    SOLVERS,
    _extract_border,
    _gravity_down,
    _gravity_left,
    _upscale_2x,
    _build_color_map,
    _apply_color_map,
    _try_tile,
    _apply_tile,
)


class TestSolvers(unittest.TestCase):
    def test_solver_registry(self):
        """Verify get_solver returns registered solver instances."""
        self.assertIn("heuristic", SOLVERS)
        self.assertIn("random", SOLVERS)
        h = get_solver("heuristic")
        self.assertIsInstance(h, HeuristicSolver)
        r = get_solver("random")
        self.assertIsInstance(r, RandomSolver)

    def test_pure_color_remapping(self):
        """Verify solver learns a 1-to-1 color permutation."""
        task = {
            "train": [
                {
                    "input": [[1, 2], [3, 0]],
                    "output": [[5, 6], [7, 0]],
                },
                {
                    "input": [[2, 1], [0, 3]],
                    "output": [[6, 5], [0, 7]],
                },
            ],
            "test": [
                {
                    "input": [[3, 2], [1, 0]],
                    "output": [[7, 6], [5, 0]],
                }
            ],
        }
        solver = HeuristicSolver()
        pred = solver.solve(task)
        expected = [[7, 6], [5, 0]]
        self.assertEqual(pred, expected)

    def test_tiling_heuristic(self):
        """Verify solver detects 2x2 grid repeating / tiling."""
        task = {
            "train": [
                {
                    "input": [[1, 2]],
                    "output": [[1, 2, 1, 2], [1, 2, 1, 2]],
                }
            ],
            "test": [
                {
                    "input": [[3, 4]],
                    "output": [[3, 4, 3, 4], [3, 4, 3, 4]],
                }
            ],
        }
        solver = HeuristicSolver()
        pred = solver.solve(task)
        expected = [[3, 4, 3, 4], [3, 4, 3, 4]]
        self.assertEqual(pred, expected)

    def test_border_extraction(self):
        """Verify border extraction heuristic on nested grids."""
        grid = [
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1],
        ]
        border = _extract_border(grid)
        self.assertEqual(border, grid)

        task = {
            "train": [
                {
                    "input": [
                        [2, 2, 2],
                        [2, 9, 2],
                        [2, 2, 2],
                    ],
                    "output": [
                        [2, 2, 2],
                        [2, 0, 2],
                        [2, 2, 2],
                    ],
                }
            ],
            "test": [
                {
                    "input": [
                        [3, 3, 3],
                        [3, 8, 3],
                        [3, 3, 3],
                    ],
                    "output": [
                        [3, 3, 3],
                        [3, 0, 3],
                        [3, 3, 3],
                    ],
                }
            ],
        }
        solver = HeuristicSolver()
        pred = solver.solve(task)
        expected = [
            [3, 3, 3],
            [3, 0, 3],
            [3, 3, 3],
        ]
        self.assertEqual(pred, expected)

    def test_gravity_down(self):
        """Verify gravity down shifts non-zero blocks to bottom."""
        inp = [
            [1, 0],
            [0, 2],
            [0, 0],
        ]
        expected = [
            [0, 0],
            [0, 0],
            [1, 2],
        ]
        self.assertEqual(_gravity_down(inp), expected)

    def test_upscale_2x(self):
        """Verify upscale 2x duplicates each cell into a 2x2 block."""
        inp = [[1, 2], [3, 4]]
        expected = [
            [1, 1, 2, 2],
            [1, 1, 2, 2],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
        ]
        self.assertEqual(_upscale_2x(inp), expected)

    def test_combined_geo_and_color(self):
        """Verify solver handles rotation + color mapping in combination."""
        task = {
            "train": [
                {
                    "input": [[1, 0], [0, 0]],
                    "output": [[0, 2], [0, 0]],  # h_flip + 1->2
                }
            ],
            "test": [
                {
                    "input": [[0, 0], [1, 0]],
                    "output": [[0, 0], [0, 2]],
                }
            ],
        }
        solver = HeuristicSolver()
        pred = solver.solve(task)
        self.assertEqual(pred, [[0, 0], [0, 2]])

    def test_random_solver_preserves_shape(self):
        """Random solver outputs matching shape with valid color values [0-9]."""
        task = {
            "train": [
                {"input": [[1, 2]], "output": [[3, 4, 5]]}
            ],
            "test": [
                {"input": [[9, 9]], "output": [[0, 0, 0]]}
            ],
        }
        solver = RandomSolver(seed=42)
        pred = solver.solve(task)
        self.assertEqual(len(pred), 1)
        self.assertEqual(len(pred[0]), 2)
        for val in pred[0]:
            self.assertIn(val, range(10))


if __name__ == "__main__":
    unittest.main()
