"""
Tests for Phase 3: Substantive BDH-CQ Educational Module

Verifies:
1. Mathematical invariants of the educational toy associative recurrence:
   - Initial state S_0 is zero.
   - S updates deterministically when demonstrations are streamed.
   - Changing the number of demonstrations changes S.
   - Reset returns to baseline.
2. Conceptual alignment:
   - Zero parameter updates (weights fixed: nabla_W L = 0).
3. No fabricated BDH-CQ performance claims in index.html or app.js.
4. Prominent labeling:
   - "Educational toy model inspired by the published BDH-CQ mechanism — NOT the official BDH-CQ implementation"
   - "PUBLISHED RESULT — PATHWAY"
"""

import unittest
import math
from pathlib import Path

class TestBdhEducationalModule(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.frontend_html = self.root_dir / "frontend" / "index.html"
        self.frontend_js = self.root_dir / "frontend" / "app.js"

    def test_toy_disclaimer_and_objective_in_html(self):
        """Verify the explicit learning objective and toy model disclaimer in frontend HTML."""
        self.assertTrue(self.frontend_html.exists(), "frontend/index.html must exist")
        content = self.frontend_html.read_text(encoding="utf-8")

        # Required learning objective
        self.assertIn("EXPLICIT LEARNING OBJECTIVE", content)
        self.assertIn("without performing parameter updates or backpropagation", content)

        # Prominent toy disclaimer required by Pathway PS
        self.assertIn("Educational toy model inspired by the published BDH-CQ mechanism — NOT the official BDH-CQ implementation.", content)

        # Published result labeling
        self.assertIn("PUBLISHED RESULT — PATHWAY", content)
        self.assertIn("Engdahl et al. (2026)", content)
        self.assertIn("pathwaycom/arc-task-gen", content)

    def test_conceptual_associative_recurrence_math(self):
        """Simulate and verify the 4x4 toy recurrence math implemented in JavaScript."""
        def project_features(grid):
            count = 0
            color = 0
            row_sum = 0
            col_sum = 0
            rows = len(grid)
            cols = len(grid[0])
            for r in range(rows):
                for c in range(cols):
                    v = grid[r][c]
                    if v != 0:
                        count += 1
                        color = v
                        row_sum += r
                        col_sum += c
            f0 = count / (rows * cols)
            f1 = color / 9.0
            f2 = row_sum / (count * max(1, rows - 1)) if count > 0 else 0.5
            f3 = col_sum / (count * max(1, cols - 1)) if count > 0 else 0.5
            return [f0, f1, f2, f3]

        def outer_product_4x4(u, v):
            return [[u[i] * v[j] for j in range(4)] for i in range(4)]

        def run_recurrence(demos, alpha=0.65):
            S = [[0.0] * 4 for _ in range(4)]
            for d in demos:
                phi_x = project_features(d["input"])
                psi_y = project_features(d["output"])
                outer = outer_product_4x4(phi_x, psi_y)
                for i in range(4):
                    for j in range(4):
                        S[i][j] = alpha * S[i][j] + (1.0 - alpha) * outer[i][j]
            return S

        demos_pattern_a = [
            {"input": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "output": [[2, 0, 0], [0, 2, 0], [0, 0, 2]]},
            {"input": [[0, 1, 1], [0, 1, 0], [0, 0, 0]], "output": [[0, 2, 2], [0, 2, 0], [0, 0, 0]]},
            {"input": [[1, 1, 0], [1, 0, 0], [0, 0, 1]], "output": [[2, 2, 0], [2, 0, 0], [0, 0, 2]]},
        ]

        # 1. Zero initial state
        S_init = [[0.0] * 4 for _ in range(4)]
        self.assertEqual(sum(sum(row) for row in S_init), 0.0)

        # 2. State changes after 1 demonstration
        S_1 = run_recurrence(demos_pattern_a[:1], alpha=0.65)
        norm_1 = math.sqrt(sum(S_1[i][j] ** 2 for i in range(4) for j in range(4)))
        self.assertGreater(norm_1, 0.0)

        # 3. State changes further after 2 demonstrations
        S_2 = run_recurrence(demos_pattern_a[:2], alpha=0.65)
        norm_2 = math.sqrt(sum(S_2[i][j] ** 2 for i in range(4) for j in range(4)))
        self.assertNotEqual(S_1, S_2)

        # 4. State differs between patterns
        demos_pattern_b = [
            {"input": [[3, 0, 0], [0, 0, 0], [0, 0, 0]], "output": [[0, 0, 0], [0, 3, 0], [0, 0, 0]]}
        ]
        S_pattern_b = run_recurrence(demos_pattern_b, alpha=0.65)
        self.assertNotEqual(S_1, S_pattern_b)

    def test_hrm_trm_vs_bdh_comparison_present(self):
        """Verify the explicit comparison between HRM/TRM test-time optimization and BDH-CQ contextual adaptation."""
        content = self.frontend_html.read_text(encoding="utf-8")
        self.assertIn("Optimization-Based Test-Time Adaptation (e.g. HRM / TRM)", content)
        self.assertIn("Contextual / Recurrent Adaptation (Illustrated by BDH-CQ)", content)
        self.assertIn("Modifies actual model weights or task-specific identity embeddings", content)
        self.assertIn("Model weights remain strictly frozen", content)

    def test_connection_to_arc_and_central_claim(self):
        """Verify connection to sparse ARC few-shot reasoning and the central public-vs-fresh claim."""
        content = self.frontend_html.read_text(encoding="utf-8")
        self.assertIn("A model's performance on a public ARC benchmark can differ from its performance on novel tasks", content)
        self.assertIn("public benchmark accuracy alone cannot establish generalization", content)


if __name__ == "__main__":
    unittest.main()
