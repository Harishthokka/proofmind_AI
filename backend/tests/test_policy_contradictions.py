import unittest
from app.schemas.analysis import DecisionStatus, EvidenceItem, EvidenceType
from app.services.decision_service import decision_service

class TestPolicyContradictions(unittest.TestCase):

    def test_a_attendance_policy_75_vs_80_conflict(self):
        """
        Test A — Attendance policy 75% versus 80%:
        CS_Policy_2025.pdf: minimum attendance requirement is 75%.
        CS_Policy_2026.pdf: minimum attendance requirement is 80%.
        Question: "What is the minimum attendance requirement for Computer Science students?"
        Expected: NEEDS_VERIFICATION, with citations to both documents.
        """
        documents = [
            {
                "filename": "CS_Policy_2025.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Computer Science Department Policy 2025: Minimum attendance requirement for Computer Science students is 75%."}],
                "freshness_date": "2025-01-15"
            },
            {
                "filename": "CS_Policy_2026.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Computer Science Department Policy 2026: Minimum attendance requirement for Computer Science students is 80%."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the minimum attendance requirement for Computer Science students?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.NEEDS_VERIFICATION)
        self.assertTrue(len(result.conflicting_evidence) >= 2)
        filenames = {ev.source_filename for ev in result.conflicting_evidence}
        self.assertIn("CS_Policy_2025.pdf", filenames)
        self.assertIn("CS_Policy_2026.pdf", filenames)

    def test_b_two_sources_agree_on_75(self):
        """
        Test B — Two relevant sources agree on 75%:
        Expected: SUPPORTED if citation and evidence checks pass.
        """
        documents = [
            {
                "filename": "CS_Policy_A.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Minimum attendance requirement for Computer Science students is 75%."}],
                "freshness_date": "2025-01-15"
            },
            {
                "filename": "CS_Policy_B.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "All Computer Science students must maintain 75% attendance to pass."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the minimum attendance requirement for Computer Science students?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)
        self.assertEqual(len(result.conflicting_evidence), 0)

    def test_c_conflict_plus_unrelated_dates_doc(self):
        """
        Test C — Attendance policy conflict plus an unrelated document containing different dates:
        The unrelated dates must not create an additional conflict.
        """
        documents = [
            {
                "filename": "CS_Policy_2025.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Minimum attendance requirement for Computer Science students is 75%."}],
                "freshness_date": "2025-01-15"
            },
            {
                "filename": "CS_Policy_2026.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Minimum attendance requirement for Computer Science students is 80%."}],
                "freshness_date": "2026-01-15"
            },
            {
                "filename": "Cafeteria_Menu_2028.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Cafeteria lunch service hours updated for 2028."}],
                "freshness_date": "2028-09-01"
            }
        ]
        question = "What is the minimum attendance requirement for Computer Science students?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.NEEDS_VERIFICATION)
        # Verify conflicting evidence belongs to CS_Policy_2025 and CS_Policy_2026, NOT Cafeteria_Menu
        filenames = {ev.source_filename for ev in result.conflicting_evidence}
        self.assertNotIn("Cafeteria_Menu_2028.pdf", filenames)

    def test_d_two_unrelated_docs_different_percentages(self):
        """
        Test D — Two unrelated documents containing different percentages:
        Must not automatically trigger NEEDS_VERIFICATION.
        """
        documents = [
            {
                "filename": "Attendance_Policy.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Minimum attendance requirement for Computer Science students is 75%."}],
                "freshness_date": "2026-01-15"
            },
            {
                "filename": "Discount_Policy.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Bookstore offers a 15% discount for faculty members."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the minimum attendance requirement for Computer Science students?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)

    def test_e_missing_or_invalid_citation(self):
        """
        Test E — Missing or invalid citation:
        Must not produce a fully supported result.
        """
        documents = [{
            "filename": "Policy.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "Valid text"}],
            "freshness_date": "2026-01-15"
        }]

        invalid_citations = [
            EvidenceItem(
                id="ev-invalid",
                source_filename="NonExistentDoc.pdf",
                page_number=99,
                source_date="2026-01-15",
                passage="Fabricated text",
                type=EvidenceType.SUPPORTING,
                confidence_score=0.90,
                citation_verified=False
            )
        ]
        self.assertFalse(decision_service.validate_citations(invalid_citations, documents))

    def test_f_reliability_score_semantics_across_statuses(self):
        """
        Test F — Reliability Score Semantics:
        1. SUPPORTED: reliability_score reflects passage text relevance score (> 0.0).
        2. NEEDS_VERIFICATION: status is NEEDS_VERIFICATION even when individual passage relevance score is high.
        3. INSUFFICIENT_EVIDENCE: reliability_score is strictly 0.0.
        """
        # Scenario 1: INSUFFICIENT_EVIDENCE -> reliability_score must be 0.0
        no_doc_res = decision_service.analyze_question("What is the attendance?", [])
        self.assertEqual(no_doc_res.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)
        self.assertEqual(no_doc_res.reliability_score, 0.0)

        # Scenario 2: SUPPORTED -> reliability_score > 0.0 matches passage relevance score
        doc_supp = [{
            "filename": "guide.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "Minimum attendance requirement is 75%."}],
            "freshness_date": "2026-01-15"
        }]
        supp_res = decision_service.analyze_question("What is the minimum attendance requirement?", doc_supp)
        self.assertEqual(supp_res.decision_status, DecisionStatus.SUPPORTED)
        self.assertGreater(supp_res.reliability_score, 0.50)

        # Scenario 3: NEEDS_VERIFICATION -> status is NEEDS_VERIFICATION
        docs_conflict = [
            {"filename": "A.pdf", "page_count": 1, "pages": [{"page_number": 1, "text": "Minimum attendance requirement is 75%."}]},
            {"filename": "B.pdf", "page_count": 1, "pages": [{"page_number": 1, "text": "Minimum attendance requirement is 80%."}]}
        ]
        conf_res = decision_service.analyze_question("What is the minimum attendance requirement?", docs_conflict)
        self.assertEqual(conf_res.decision_status, DecisionStatus.NEEDS_VERIFICATION)

if __name__ == '__main__':
    unittest.main()
