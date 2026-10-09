import unittest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.services.db_service import db_service

class TestUserIsolationSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        import uuid
        uid = uuid.uuid4().hex[:6]
        # Register User A
        email_a = f"usera_{uid}@example.com"
        res_a = cls.client.post(
            "/api/v1/auth/register",
            json={"email": email_a, "full_name": "User A", "password": "Password123!"}
        )
        cls.token_a = res_a.json()["token"]
        cls.user_a_id = res_a.json()["user"]["id"]
        cls.headers_a = {"Authorization": f"Bearer {cls.token_a}"}

        # Register User B
        email_b = f"userb_{uid}@example.com"
        res_b = cls.client.post(
            "/api/v1/auth/register",
            json={"email": email_b, "full_name": "User B", "password": "Password123!"}
        )
        cls.token_b = res_b.json()["token"]
        cls.user_b_id = res_b.json()["user"]["id"]
        cls.headers_b = {"Authorization": f"Bearer {cls.token_b}"}

    def test_01_user_a_creates_resources(self):
        # User A uploads a PDF document
        pdf_content = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref 0 %%EOF"
        res_upload = self.client.post(
            "/api/v1/documents/upload",
            headers=self.headers_a,
            files={"file": ("usera_private_doc.pdf", io.BytesIO(pdf_content), "application/pdf")}
        )
        self.assertEqual(res_upload.status_code, 200)
        TestUserIsolationSecurity.doc_a_id = res_upload.json()["document_id"]

        # User A creates a conversation
        res_conv = self.client.post(
            "/api/v1/conversations",
            headers=self.headers_a,
            json={"title": "User A Private Conversation", "document_ids": [self.doc_a_id]}
        )
        self.assertEqual(res_conv.status_code, 200)
        TestUserIsolationSecurity.conv_a_id = res_conv.json()["id"]

        # User A runs an analysis
        res_ans = self.client.post(
            "/api/v1/analysis/run",
            headers=self.headers_a,
            json={"question": "What is in User A document?", "document_ids": [self.doc_a_id]}
        )
        self.assertEqual(res_ans.status_code, 200)
        TestUserIsolationSecurity.ans_a_id = res_ans.json()["id"]

    def test_02_user_b_cannot_list_user_a_documents(self):
        res = self.client.get("/api/v1/documents", headers=self.headers_b)
        self.assertEqual(res.status_code, 200)
        doc_ids = [d["id"] for d in res.json()]
        self.assertNotIn(self.doc_a_id, doc_ids)

    def test_03_user_b_cannot_delete_user_a_document(self):
        res = self.client.delete(f"/api/v1/documents/{self.doc_a_id}", headers=self.headers_b)
        self.assertEqual(res.status_code, 403)

    def test_04_unauthenticated_cannot_delete_user_a_document(self):
        res = self.client.delete(f"/api/v1/documents/{self.doc_a_id}")
        self.assertEqual(res.status_code, 403)

    def test_05_user_b_cannot_access_user_a_conversation(self):
        res = self.client.get(f"/api/v1/conversations/{self.conv_a_id}", headers=self.headers_b)
        self.assertEqual(res.status_code, 404)

    def test_06_user_b_cannot_post_message_to_user_a_conversation(self):
        res = self.client.post(
            f"/api/v1/conversations/{self.conv_a_id}/messages",
            headers=self.headers_b,
            json={"question": "Unauthorized question?"}
        )
        self.assertEqual(res.status_code, 404)

    def test_07_user_b_cannot_upload_and_reanalyze_in_user_a_conversation(self):
        pdf_content = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref 0 %%EOF"
        res = self.client.post(
            f"/api/v1/conversations/{self.conv_a_id}/upload-and-reanalyze",
            headers=self.headers_b,
            files={"file": ("malicious.pdf", io.BytesIO(pdf_content), "application/pdf")},
            data={"original_question": "Hack user A?"}
        )
        self.assertEqual(res.status_code, 404)

    def test_08_user_b_cannot_delete_user_a_conversation(self):
        res = self.client.delete(f"/api/v1/conversations/{self.conv_a_id}", headers=self.headers_b)
        self.assertEqual(res.status_code, 404)

    def test_09_user_b_history_does_not_contain_user_a_analysis(self):
        res = self.client.get("/api/v1/analysis/history", headers=self.headers_b)
        self.assertEqual(res.status_code, 200)
        history_ids = [item["id"] for item in res.json()]
        self.assertNotIn(self.ans_a_id, history_ids)

    def test_10_user_b_cannot_analyze_user_a_document_by_id(self):
        res = self.client.post(
            "/api/v1/analysis/run",
            headers=self.headers_b,
            json={"question": "Tell me about user A data", "document_ids": [self.doc_a_id]}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["decision_status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(len(data["supporting_evidence"]), 0)

if __name__ == "__main__":
    unittest.main()
