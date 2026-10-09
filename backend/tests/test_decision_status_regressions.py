import unittest
import pymupdf
from app.services.decision_service import decision_service

def make_doc_record(doc_id: str, filename: str, text: str) -> dict:
    return {
        "id": doc_id,
        "filename": filename,
        "owner_user_id": "test-user",
        "file_size": len(text),
        "page_count": 1,
        "total_chars": len(text),
        "pages": [{"page_number": 1, "text": text}],
        "summary": text[:50],
        "status": "PROCESSED",
        "freshness_date": "2026-10-09",
        "uploaded_at": "2026-10-09 21:00:00"
    }

class TestDecisionStatusRegressions(unittest.TestCase):
    def test_01_supported_status(self):
        doc = make_doc_record("doc-1", "policy.pdf", "The annual vacation allowance for full-time employees is 20 business days.")
        res = decision_service.analyze_question("What is the annual vacation allowance?", [doc])
        self.assertEqual(res.decision_status, "SUPPORTED")
        self.assertTrue(len(res.supporting_evidence) > 0)

    def test_02_needs_verification_on_contradiction(self):
        # Doc 1 says 20 days, Doc 2 says 15 days for full-time employees
        doc1 = make_doc_record("doc-1", "hr_policy_2025.pdf", "The annual vacation allowance for full-time employees is 20 business days.")
        doc2 = make_doc_record("doc-2", "hr_policy_2026.pdf", "The annual vacation allowance for full-time employees is 15 business days.")
        
        res = decision_service.analyze_question("What is the annual vacation allowance for full-time employees?", [doc1, doc2])
        self.assertEqual(res.decision_status, "NEEDS_VERIFICATION")
        self.assertTrue(len(res.conflicting_evidence) > 0)

    def test_03_insufficient_evidence_status(self):
        doc = make_doc_record("doc-1", "policy.pdf", "The annual vacation allowance for full-time employees is 20 business days.")
        res = decision_service.analyze_question("What is the maximum remote work budget reimbursement?", [doc])
        self.assertEqual(res.decision_status, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(len(res.supporting_evidence), 0)

if __name__ == "__main__":
    unittest.main()
