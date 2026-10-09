import unittest
from app.schemas.analysis import DecisionStatus
from app.services.retrieval_service import retrieval_service
from app.services.decision_service import decision_service

class TestRetrievalQuality(unittest.TestCase):

    def test_phase3_a_five_vs_direct(self):
        """
        TEST A:
        Question: What are the Five Vs of Big Data?
        Expected: Retrieve the passage listing the five Vs.
        """
        documents = [{
            "filename": "big_data_architecture.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."}],
            "freshness_date": "2026-01-15"
        }]
        question = "What are the Five Vs of Big Data?"
        evidence = retrieval_service.retrieve_evidence(question, documents)

        self.assertTrue(len(evidence) > 0)
        self.assertIn("Volume, Velocity, Variety, Veracity, and Value", evidence[0].passage)
        self.assertEqual(evidence[0].source_filename, "big_data_architecture.pdf")
        self.assertEqual(evidence[0].page_number, 1)

    def test_phase3_b_different_wording_synonym(self):
        """
        TEST B:
        Question: Explain the five characteristics of Big Data.
        Expected: Retrieve the same relevant passage despite different wording ("characteristics" vs "Vs").
        """
        documents = [{
            "filename": "big_data_architecture.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."}],
            "freshness_date": "2026-01-15"
        }]
        question = "Explain the five characteristics of Big Data."
        evidence = retrieval_service.retrieve_evidence(question, documents)

        self.assertTrue(len(evidence) > 0)
        self.assertIn("Volume, Velocity, Variety, Veracity, and Value", evidence[0].passage)

    def test_phase3_c_data_quality_checks(self):
        """
        TEST C:
        Question: What data-quality checks are recommended?
        Expected: Retrieve the relevant data-quality section.
        """
        documents = [{
            "filename": "data_governance_guide.pdf",
            "page_count": 3,
            "pages": [
                {"page_number": 1, "text": "Introduction to enterprise data strategy."},
                {"page_number": 2, "text": "Recommended data-quality checks include schema validation, null checks, and duplicate removal."},
                {"page_number": 3, "text": "Storage options include S3 and HDFS."}
            ],
            "freshness_date": "2026-01-15"
        }]
        question = "What data-quality checks are recommended?"
        evidence = retrieval_service.retrieve_evidence(question, documents)

        self.assertTrue(len(evidence) > 0)
        self.assertIn("schema validation, null checks, and duplicate removal", evidence[0].passage)
        self.assertEqual(evidence[0].page_number, 2)

    def test_phase3_d_unsupported_entity_query(self):
        """
        TEST D:
        Question: What percentage of companies use Apache Spark?
        Expected: No supporting evidence if the uploaded documents do not provide this information.
        """
        documents = [{
            "filename": "employee_handbook.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "All employees must display identification badges at security checkpoints."}],
            "freshness_date": "2026-01-15"
        }]
        question = "What percentage of companies use Apache Spark?"
        evidence = retrieval_service.retrieve_evidence(question, documents)

        self.assertEqual(len(evidence), 0, "No evidence should be retrieved for unmentioned entities.")
        
        result = decision_service.analyze_question(question, documents)
        self.assertEqual(result.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)

    def test_phase3_e_multi_document_relevance_isolation(self):
        """
        TEST E:
        Upload two PDFs containing unrelated topics (Doc A: Attendance Policy, Doc B: Cafeteria Menu).
        Expected: Evidence for a question should be relevant to the question, not merely present in an uploaded document.
        """
        documents = [
            {
                "filename": "Attendance_Policy.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Students must maintain a minimum of 75% attendance to attend final exams."}],
                "freshness_date": "2026-01-15"
            },
            {
                "filename": "Cafeteria_Menu.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The campus cafeteria serves breakfast starting at 8:00 AM daily."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the attendance requirement?"
        evidence = retrieval_service.retrieve_evidence(question, documents)

        self.assertTrue(len(evidence) > 0)
        # All retrieved evidence items must belong strictly to Attendance_Policy.pdf
        for ev in evidence:
            self.assertEqual(ev.source_filename, "Attendance_Policy.pdf")
            self.assertNotIn("cafeteria", ev.passage.lower())

if __name__ == '__main__':
    unittest.main()
