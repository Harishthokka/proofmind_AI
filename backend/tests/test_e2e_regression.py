import unittest
import io
import fitz
from app.schemas.analysis import DecisionStatus, EvidenceItem, EvidenceType
from app.services.pdf_service import pdf_service
from app.services.decision_service import decision_service

class TestE2ERegressionSuite(unittest.TestCase):

    def test_e2e_a_valid_supported_answer(self):
        """
        TEST A — Valid supported answer
        Upload the Big Data demo PDF.
        Ask: "What are the Five Vs of Big Data?"
        Expected: SUPPORTED, with citations to actual supporting passages.
        """
        documents = [{
            "filename": "Big_Data_Overview.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."}],
            "freshness_date": "2026-01-15"
        }]
        question = "What are the Five Vs of Big Data?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)
        self.assertTrue(len(result.supporting_evidence) > 0)
        self.assertEqual(result.supporting_evidence[0].source_filename, "Big_Data_Overview.pdf")
        self.assertEqual(result.supporting_evidence[0].page_number, 1)

    def test_e2e_b_paraphrased_question(self):
        """
        TEST B — Paraphrased question
        Ask: "What are the five main characteristics of Big Data?"
        Expected: Retrieve the relevant evidence and return SUPPORTED if the document supports the answer.
        """
        documents = [{
            "filename": "Big_Data_Overview.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."}],
            "freshness_date": "2026-01-15"
        }]
        question = "What are the five main characteristics of Big Data?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)
        self.assertTrue(len(result.supporting_evidence) > 0)

    def test_e2e_c_unsupported_fact(self):
        """
        TEST C — Unsupported fact
        Ask: "What percentage of companies use Apache Spark?"
        Expected: INSUFFICIENT_EVIDENCE if the uploaded documents do not state this information.
        The system must not invent a percentage.
        """
        documents = [{
            "filename": "attendance_policy.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "Students must maintain 75% attendance."}],
            "freshness_date": "2026-01-15"
        }]
        question = "What percentage of companies use Apache Spark?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)
        self.assertEqual(len(result.supporting_evidence), 0)
        self.assertIn("No matching evidence found", result.grounded_answer)

    def test_e2e_d_genuine_contradiction(self):
        """
        TEST D — Genuine contradiction
        Upload two documents that explicitly give different attendance requirements for the same applicable context.
        Ask about the required attendance percentage.
        Expected: NEEDS_VERIFICATION, with citations to both conflicting passages.
        """
        documents = [
            {
                "filename": "CS_Policy_A.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The CS Department minimum attendance requirement is 75%."}],
                "freshness_date": "2026-01-15"
            },
            {
                "filename": "CS_Policy_B.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The CS Department minimum attendance requirement is 80%."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the minimum attendance requirement?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.NEEDS_VERIFICATION)
        self.assertTrue(len(result.conflicting_evidence) >= 2)
        filenames = {ev.source_filename for ev in result.conflicting_evidence}
        self.assertIn("CS_Policy_A.pdf", filenames)
        self.assertIn("CS_Policy_B.pdf", filenames)

    def test_e2e_e_irrelevant_conflict(self):
        """
        TEST E — Irrelevant conflict
        Upload two documents containing unrelated conflicting numbers or dates.
        Ask a question unrelated to those conflicts.
        Expected: The unrelated conflict must not trigger NEEDS_VERIFICATION.
        """
        documents = [
            {
                "filename": "big_data_2024.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "The five Vs of Big Data are Volume, Velocity, Variety, Veracity, and Value."}],
                "freshness_date": "2024-01-01"
            },
            {
                "filename": "cafeteria_2026.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Cafeteria meal cost is $15 per student."}],
                "freshness_date": "2026-01-01"
            }
        ]
        question = "What are the Five Vs of Big Data?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)

    def test_e2e_f_invalid_citation(self):
        """
        TEST F — Invalid citation
        Attempt to return a citation with a nonexistent document ID, invalid page number, or passage that does not exist in source text.
        Expected: The invalid citation must not be presented as a verified citation or used to justify SUPPORTED.
        """
        documents = [{
            "filename": "policy.pdf",
            "page_count": 2,
            "pages": [{"page_number": 1, "text": "Valid source text content."}],
            "freshness_date": "2026-01-15"
        }]
        
        # Test nonexistent passage text
        fake_evidence = [
            EvidenceItem(
                id="ev-fake",
                source_filename="policy.pdf",
                page_number=1,
                source_date="2026-01-15",
                passage="Fabricated text that never existed in the PDF file.",
                type=EvidenceType.SUPPORTING,
                confidence_score=0.9,
                citation_verified=True
            )
        ]
        self.assertFalse(decision_service.validate_citations(fake_evidence, documents))

    def test_e2e_g_multi_document_isolation(self):
        """
        TEST G — Multi-document isolation
        Upload two unrelated PDFs. Ask a question answered by only one document.
        Expected: The answer relies on evidence from the correct document, not unrelated passages.
        """
        documents = [
            {
                "filename": "Attendance.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Students must maintain 75% attendance."}],
                "freshness_date": "2026-01-15"
            },
            {
                "filename": "Library.pdf",
                "page_count": 1,
                "pages": [{"page_number": 1, "text": "Library books can be checked out for 14 days."}],
                "freshness_date": "2026-01-15"
            }
        ]
        question = "What is the library book checkout duration?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.SUPPORTED)
        self.assertEqual(len(result.supporting_evidence), 1)
        self.assertEqual(result.supporting_evidence[0].source_filename, "Library.pdf")

    def test_e2e_h_empty_or_unreadable_pdf(self):
        """
        TEST H — Empty or unreadable PDF
        Verify the behavior for an empty, malformed, or image-only PDF.
        Expected: Clear error or insufficient-text result without a fabricated answer.
        """
        # Test 1: Invalid PDF signature bytes
        with self.assertRaises(ValueError):
            pdf_service.extract_text_and_metadata(b"Not a PDF file content", "bad.pdf")

        # Test 2: Corrupted PDF bytes starting with %PDF-
        with self.assertRaises(ValueError):
            pdf_service.extract_text_and_metadata(b"%PDF-1.4 corrupt pdf dummy stream", "corrupt.pdf")

        # Test 3: Zero-text / blank PDF page
        doc = fitz.open()
        doc.new_page()  # Blank page without text
        blank_pdf_bytes = doc.tobytes()
        doc.close()

        result = pdf_service.extract_text_and_metadata(blank_pdf_bytes, "scanned_image.pdf")
        self.assertEqual(result["status"], "NO_TEXT_EXTRACTED")
        self.assertIn("No extractable text found", result["summary"])

    def test_e2e_i_multiple_questions_isolation(self):
        """
        TEST I — Multiple questions
        Run several questions against the same uploaded document.
        Verify evidence from one analysis does not incorrectly contaminate another analysis.
        """
        documents = [{
            "filename": "university_rules.pdf",
            "page_count": 2,
            "pages": [
                {"page_number": 1, "text": "Attendance requirement is 75% for all registered courses."},
                {"page_number": 2, "text": "Library fine is $2 per day for overdue items."}
            ],
            "freshness_date": "2026-01-15"
        }]

        q1_result = decision_service.analyze_question("What is the attendance requirement?", documents)
        q2_result = decision_service.analyze_question("What is the library fine?", documents)

        self.assertEqual(q1_result.decision_status, DecisionStatus.SUPPORTED)
        self.assertEqual(q1_result.supporting_evidence[0].page_number, 1)

        self.assertEqual(q2_result.decision_status, DecisionStatus.SUPPORTED)
        self.assertEqual(q2_result.supporting_evidence[0].page_number, 2)
        self.assertNotIn("75%", q2_result.supporting_evidence[0].passage)

if __name__ == '__main__':
    unittest.main()
