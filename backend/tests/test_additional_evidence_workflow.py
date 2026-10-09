import unittest
import io
import uuid
import pypdf
from fastapi.testclient import TestClient
from app.main import app

import fitz

def create_pdf_bytes(text_content: str) -> bytes:
    """Helper to generate a valid PDF byte stream with provided text content using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), text_content)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

class TestAdditionalEvidenceWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        uid = uuid.uuid4().hex[:6]
        res = cls.client.post(
            "/api/v1/auth/register",
            json={"email": f"workflow_{uid}@proofmind.ai", "full_name": "Workflow User", "password": "Password123!"}
        )
        cls.token = res.json()["token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_01_upload_and_reanalyze_workflow(self):
        # 1. Create a conversation
        res_conv = self.client.post(
            "/api/v1/conversations",
            headers=self.headers,
            json={"title": "Scholarship Eligibility Workspace"}
        )
        conv_id = res_conv.json()["id"]

        # 2. Upload Document 1 (General rules, lacks family income limit)
        doc1_text = "Merit Scholarship Guidelines: Applicants must maintain a 3.8 GPA and complete 50 community service hours."
        pdf1 = create_pdf_bytes(doc1_text)
        
        # Submit initial question to conversation
        q = "What is the maximum family income limit for the merit scholarship?"
        res_msg1 = self.client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            headers=self.headers,
            json={"question": q}
        )
        self.assertEqual(res_msg1.status_code, 200)
        data1 = res_msg1.json()
        self.assertEqual(data1["decision_status"], "INSUFFICIENT_EVIDENCE")
        self.assertIsNotNone(data1.get("missing_information"))

        # 3. Upload Document 2 (Supplies missing family income limit) via upload-and-reanalyze
        doc2_text = "Merit Scholarship Financial Criteria: The maximum family income limit for the merit scholarship is $60,000 per year."
        pdf2 = create_pdf_bytes(doc2_text)

        res_reanalyze = self.client.post(
            f"/api/v1/conversations/{conv_id}/upload-and-reanalyze",
            headers=self.headers,
            files={"file": ("financial_rules.pdf", pdf2, "application/pdf")},
            data={"original_question": q}
        )
        self.assertEqual(res_reanalyze.status_code, 200)
        data2 = res_reanalyze.json()

        # 4. Verify decision status is now SUPPORTED
        self.assertEqual(data2["decision_status"], "SUPPORTED")
        self.assertIn("$60,000", data2["grounded_answer"])
        self.assertTrue(len(data2["supporting_evidence"]) > 0)
        self.assertEqual(data2["supporting_evidence"][0]["source_filename"], "financial_rules.pdf")

    def test_02_unresolving_document_remains_insufficient(self):
        # 1. Create conversation
        res_conv = self.client.post(
            "/api/v1/conversations",
            headers=self.headers,
            json={"title": "Unrelated Document Test"}
        )
        conv_id = res_conv.json()["id"]

        q = "What is the maximum family income limit for the merit scholarship?"

        # 2. Upload Document 3 (Contains unrelated info about campus library hours)
        doc3_text = "Campus Library Hours: The main library opens at 8:00 AM and closes at 10:00 PM on weekdays."
        pdf3 = create_pdf_bytes(doc3_text)

        res_reanalyze = self.client.post(
            f"/api/v1/conversations/{conv_id}/upload-and-reanalyze",
            headers=self.headers,
            files={"file": ("library_hours.pdf", pdf3, "application/pdf")},
            data={"original_question": q}
        )
        self.assertEqual(res_reanalyze.status_code, 200)
        data3 = res_reanalyze.json()

        # 3. Verify status remains INSUFFICIENT_EVIDENCE
        self.assertEqual(data3["decision_status"], "INSUFFICIENT_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
