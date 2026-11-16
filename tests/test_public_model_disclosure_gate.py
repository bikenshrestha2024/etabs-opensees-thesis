"""Public model evidence metadata gate. No real project content."""
import unittest
from tools.audit_public_model_disclosure import review


class PublicationBoundaryTests(unittest.TestCase):
    def test_generated_viewer_and_schema_docs_are_blocked(self):
        result=review([
            "components/model/assembly.py",
            "Viewer_Preview_V141/OpenSees_Element_Connectivity_3D.html",
            "New_Export_Viewer_Diagnostic/OpenSees_Source_Model_Metadata_V118.json",
            "docs/json/files/Viewer_Preview_V141/OpenSees_Element_Connectivity.json.md",
        ])
        self.assertEqual(result["status"],"BLOCKED_CURRENT_PUBLIC_TRACKING")
        self.assertEqual(len(result["forbidden_paths"]),2)
        self.assertTrue(result["history_review_required"])

    def test_historic_model_candidates_remain_a_manual_decision(self):
        result=review([
            "components/gravity/solver_stack.py",
            "Worked_Example_V138/example/OpenSees_Complete_Model_Data_V118.json",
            "tests/test_gravity_full_source_reactions.py",
        ])
        self.assertEqual(result["status"],"NO_FORBIDDEN_VIEWER_FILES_IN_CURRENT_INDEX")
        self.assertEqual(len(result["other_model_candidates_need_manual_review"]),1)
        self.assertFalse(result["content_review_performed"])


if __name__=="__main__":
    unittest.main(verbosity=2)
