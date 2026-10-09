import unittest
import uuid
import io
import fitz
from app.services.auth_service import auth_service
from app.services.db_service import db_service
from app.services.decision_service import decision_service
from app.schemas.analysis import DecisionStatus

class TestPhase1To7Extensions(unittest.TestCase):

    def test_01_user_registration_and_authentication(self):
        """Phase 1: Registration, Login, Token generation, and Password Hashing."""
        unique_id = uuid.uuid4().hex[:6]
        email = f"alice_{unique_id}@example.com"
        password = "SecurePassword123!"

        # Register User
        res = auth_service.register_user(email, "Alice Smith", password)
        self.assertIn("token", res)
        self.assertEqual(res["user"]["email"], email)

        # Authenticate Token
        user = auth_service.get_user_from_token(res["token"])
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], email)

        # Login User
        login_res = auth_service.authenticate_user(email, password)
        self.assertIn("token", login_res)

        # Invalid Password Rejection
        with self.assertRaises(ValueError):
            auth_service.authenticate_user(email, "WrongPassword!")

    def test_02_document_user_isolation(self):
        """Phase 2 & Phase 7: Document Owner Isolation."""
        unique_id = uuid.uuid4().hex[:6]
        user1 = auth_service.register_user(f"u1_{unique_id}@example.com", "User One", "pass123456")["user"]
        user2 = auth_service.register_user(f"u2_{unique_id}@example.com", "User Two", "pass123456")["user"]

        doc1_record = {
            "id": f"doc-u1-{unique_id}",
            "owner_user_id": user1["id"],
            "filename": "User1_Private.pdf",
            "storage_filename": f"doc-u1-{unique_id}_User1_Private.pdf",
            "file_size": 100,
            "page_count": 1,
            "total_chars": 50,
            "pages": [{"page_number": 1, "text": "Confidential data for User 1 only."}],
            "summary": "Private doc",
            "status": "PROCESSED",
            "uploaded_at": "2026-01-15 10:00:00"
        }
        db_service.save_document(doc1_record)

        # User 1 can retrieve own document
        u1_docs = db_service.get_user_documents(user1["id"])
        self.assertEqual(len(u1_docs), 1)
        self.assertEqual(u1_docs[0]["filename"], "User1_Private.pdf")

        # User 2 cannot retrieve User 1's document
        u2_docs = db_service.get_user_documents(user2["id"])
        self.assertEqual(len(u2_docs), 0)

    def test_03_missing_information_identification(self):
        """Phase 5: Identify Missing Information when evidence is insufficient."""
        documents = [{
            "filename": "Scholarship_Academic_Policy.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "Scholarship requires a minimum GPA of 3.8 and 100 hours of community service."}],
            "freshness_date": "2026-01-15"
        }]

        question = "What is the family-income limit for this scholarship?"
        result = decision_service.analyze_question(question, documents)

        self.assertEqual(result.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)
        self.assertIsNotNone(result.missing_information)
        self.assertIsNotNone(result.suggested_doc_request)
        self.assertIn("family-income", result.missing_information.lower())
        self.assertIn("upload", result.suggested_doc_request.lower())

    def test_04_reanalysis_with_additional_document(self):
        """Phase 6: Reanalysis when additional document is provided."""
        doc1 = {
            "filename": "Scholarship_Academic_Policy.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "Scholarship requires a minimum GPA of 3.8 and 100 hours of community service."}],
            "freshness_date": "2026-01-15"
        }

        doc2 = {
            "filename": "Scholarship_Financial_Criteria.pdf",
            "page_count": 1,
            "pages": [{"page_number": 1, "text": "The family-income eligibility limit for the scholarship is $60,000 per year."}],
            "freshness_date": "2026-01-15"
        }

        question = "What is the family-income limit for this scholarship?"

        # Initial Analysis (Doc 1 only) -> INSUFFICIENT_EVIDENCE
        res1 = decision_service.analyze_question(question, [doc1])
        self.assertEqual(res1.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)

        # Re-analysis (Doc 1 + Doc 2) -> SUPPORTED
        res2 = decision_service.analyze_question(question, [doc1, doc2])
        self.assertEqual(res2.decision_status, DecisionStatus.SUPPORTED)
        self.assertTrue(len(res2.supporting_evidence) > 0)
        self.assertEqual(res2.supporting_evidence[0].source_filename, "Scholarship_Financial_Criteria.pdf")

if __name__ == '__main__':
    unittest.main()
