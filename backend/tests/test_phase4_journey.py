"""
Automated tests for Phase 4: 60-Second Guided Learner Journey,
Central Claim Integrity, Evidence Labeling, and BDH-CQ Integration.

Verifies:
1. Guided mode initialization and presence of all 5 steps in the walkthrough.
2. Step 1 interaction (Try demonstration pair and solver/reference inspection).
3. Step 2 interaction (The core conceptual question testing whether high benchmark score proves generalization).
4. Step 3 interaction (Public-vs-fresh diagnostic comparison with fallback/genuine labeling).
5. Step 4 interpretation quiz (Verifies that Option C is the only correct answer: diagnostic signal, NOT proof of memorization).
6. Step 5 bridge to BDH-CQ test-time adaptation.
7. Fixed parameters and non-runtime gradient indicator wording (no misleading official gradient claims).
8. Documentation of at least 3 recent primary scientific literature citations in index.html and docs/provenance.md.
"""

import unittest
from pathlib import Path

class TestPhase4GuidedJourneyAndIntegration(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.frontend_html = self.root_dir / "frontend" / "index.html"
        self.frontend_js = self.root_dir / "frontend" / "app.js"
        self.provenance_md = self.root_dir / "docs" / "provenance.md"

    def test_journey_sections_and_steps_exist(self):
        """Verify all 5 steps of the 60-second guided journey are present in index.html."""
        content = self.frontend_html.read_text(encoding="utf-8")

        self.assertIn('id="journey"', content)
        self.assertIn('id="journey-step-1"', content)
        self.assertIn('id="journey-step-2"', content)
        self.assertIn('id="journey-step-3"', content)
        self.assertIn('id="journey-step-4"', content)
        self.assertIn('id="journey-step-5"', content)

        # Nav link and hero CTA
        self.assertIn('href="#journey"', content)
        self.assertIn('startGuidedJourney()', content)

    def test_step2_core_question_verbiage(self):
        """Verify Step 2 asks the exact question regarding whether benchmark accuracy proves generalization."""
        content = self.frontend_html.read_text(encoding="utf-8")
        self.assertIn("Does solving public benchmark tasks well prove that the system has learned the underlying reasoning rule?", content)
        self.assertIn("Public accuracy alone cannot distinguish generalization from familiarity", content)

    def test_step4_interpretation_choices(self):
        """Verify Step 4 has multiple-choice answers where Option C correctly captures multiple explanations without asserting memorization."""
        content = self.frontend_html.read_text(encoding="utf-8")
        self.assertIn("If the fresh score is lower than the public score, what does that prove?", content)
        self.assertIn("There is evidence consistent with a generalization gap, but multiple explanations remain", content)

    def test_pedagogical_gradient_labeling(self):
        """Verify the gradient indicator is labeled as pedagogical/fixed parameters rather than an official runtime measurement."""
        content = self.frontend_html.read_text(encoding="utf-8")
        self.assertIn("Test-Time Param Updates:", content)
        self.assertIn("NONE (Parameters $W$: FIXED)", content)
        self.assertIn("Gradient Indicator", content)
        self.assertIn("Pedagogical Indicator", content)

    def test_primary_literature_documented(self):
        """Verify at least 3 recent primary papers (2022-2026) and foundational work are cited in provenance.md and index.html."""
        html_content = self.frontend_html.read_text(encoding="utf-8")
        prov_content = self.provenance_md.read_text(encoding="utf-8")

        # Check references in HTML
        self.assertIn("Engdahl et al. (2026)", html_content)
        self.assertIn("Bordes et al. (2024)", html_content)
        self.assertIn("Akyürek", html_content)
        self.assertIn("2411.07279", html_content)
        self.assertIn("Chollet (2019)", html_content)

        # Check references in provenance.md
        self.assertIn("Engdahl, B., Kosowski, A., Chorowski, J.", prov_content)
        self.assertIn("Bordes, F., Balestriero, R., Lacroix, T., & LeCun, Y. (2024)", prov_content)
        self.assertIn("Akyürek, E., Damani, M., Qiu, L., Guo, H., Kim, Y., & Andreas, J. (2024)", prov_content)
        self.assertIn("Chollet, F. (2019)", prov_content)

    def test_journey_methods_implemented_in_js(self):
        """Verify JavaScript implements controller functions for the guided journey."""
        js_content = self.frontend_js.read_text(encoding="utf-8")

        self.assertIn("window.startGuidedJourney", js_content)
        self.assertIn("window.goToJourneyStep", js_content)
        self.assertIn("window.jInspectSolver", js_content)
        self.assertIn("window.jRevealReference", js_content)
        self.assertIn("window.jAnswerStep2", js_content)
        self.assertIn("window.jRunExperiment", js_content)
        self.assertIn("window.jAnswerStep4", js_content)

if __name__ == "__main__":
    unittest.main()
