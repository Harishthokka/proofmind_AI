import unittest
from app.schemas.analysis import DecisionStatus, EvidenceItem, EvidenceType
from app.services.decision_service import decision_service

class TestEvidenceClassification(unittest.TestCase):

    def test_a_direct_factual_question(self):
        """
        TEST A — Direct factual question:
        Document: "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."
        Question: "What are the Five Vs of Big Data?"
        Expected: SUPPORTED if the evidence and citations pass validation.
        """
        documents = [{
            "filename": "big_data_guide.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."}],
            "freshness_date": "2026-01-15"
        }]
        question = "What are the Five Vs of Big Data?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)
        self.assertIn("Volume, Velocity, Variety, Veracity, and Value", result.grounded_answer)
        self.assertTrue(len(result.supporting_evidence) > 0)

    def test_b_unrelated_statements(self):
        """
        TEST B — Unrelated statements:
        Document A: "Students must maintain 75% attendance."
        Document B: "The orientation tour is optional."
        Question: "What is the attendance requirement?"
        Expected: SUPPORTED if no relevant contradiction exists.
        """
        documents = [
            {
                "filename": "attendance_policy.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Students must maintain 75% attendance."}],
                "freshness_date": "2026-01-15"
            },
            {
                "filename": "orientation_guide.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The orientation tour is optional."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the attendance requirement?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)
        self.assertEqual(len(result.conflicting_evidence), 0)

    def test_c_relevant_conflict(self):
        """
        TEST C — Relevant conflict:
        Document A: "The minimum attendance requirement is 75%."
        Document B: "The minimum attendance requirement is 80%."
        Question: "What is the minimum attendance requirement?"
        Expected: NEEDS_VERIFICATION if the applicable policy cannot be established.
        """
        documents = [
            {
                "filename": "policy_2025.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The minimum attendance requirement is 75%."}],
                "freshness_date": "2025-01-15"
            },
            {
                "filename": "policy_2026.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The minimum attendance requirement is 80%."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the minimum attendance requirement?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.NEEDS_VERIFICATION)
        self.assertTrue(len(result.conflicting_evidence) > 0)

    def test_d_unrelated_dates(self):
        """
        TEST D — Unrelated dates:
        Document A has a 2024 issue date and contains the Five Vs of Big Data.
        Document B has a 2026 issue date and describes a different, unrelated subject.
        Question: "What are the Five Vs of Big Data?"
        Expected: SUPPORTED if relevant evidence is sufficient and validated.
        """
        documents = [
            {
                "filename": "big_data_2024.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."}],
                "freshness_date": "2024-05-10"
            },
            {
                "filename": "unrelated_2026.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The cafeteria menu opens at 8:00 AM daily."}],
                "freshness_date": "2026-09-01"
            }
        ]
        question = "What are the Five Vs of Big Data?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)

    def test_e_missing_evidence(self):
        """
        TEST E — Missing evidence:
        Question: "What percentage of companies use Apache Spark?"
        Neither uploaded document contains this information.
        Expected: INSUFFICIENT_EVIDENCE.
        """
        documents = [
            {
                "filename": "company_rules.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Employees must wear identification badges at all times."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What percentage of companies use Apache Spark?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)

    def test_f_citation_validation(self):
        """
        TEST F — Citation validation:
        A generated answer cites a nonexistent page or unsupported passage.
        Expected: The system must not classify the answer as SUPPORTED.
        """
        documents = [
            {
                "filename": "policy.pdf",
                "page_count": 2,
                "pages": [{"page_number": 1, "text": "Valid text"}],
                "freshness_date": "2026-01-15"
            }
        ]
        invalid_evidence = [
            EvidenceItem(
                id="ev-invalid-1",
                source_filename="policy.pdf",
                page_number=99,  # Exceeds page_count (2)
                source_date="2026-01-15",
                passage="Invalid page reference",
                type=EvidenceType.SUPPORTING,
                confidence_score=0.9,
                citation_verified=True,
                verification_note="Invalid page"
            )
        ]
        valid_citations = decision_service.validate_citations(invalid_evidence, documents)
        self.assertFalse(valid_citations, "Citations targeting page 99 in a 2-page doc must fail validation.")

if __name__ == '__main__':
    unittest.main()
