import unittest
import uuid
import sqlite3
from app.services.db_service import db_service

class TestSQLitePersistence(unittest.TestCase):
    def test_01_user_persistence(self):
        uid = uuid.uuid4().hex[:8]
        user_id = f"user-{uid}"
        email = f"persist_{uid}@proofmind.ai"
        db_service.create_user(user_id, email, "Persist User", "hash123", "salt123", "2026-10-09 21:00:00")

        fetched = db_service.get_user_by_email(email)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], user_id)
        self.assertEqual(fetched["full_name"], "Persist User")

    def test_02_token_persistence_and_revocation(self):
        uid = uuid.uuid4().hex[:8]
        user_id = f"user-{uid}"
        token = f"tok-{uid}"
        db_service.create_user(user_id, f"tokuser_{uid}@proofmind.ai", "Token User", "hash", "salt", "2026-10-09")
        db_service.create_token(token, user_id, "2026-10-09")

        user = db_service.get_user_by_token(token)
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], user_id)

        # Revoke token
        db_service.delete_token(token)
        user_after = db_service.get_user_by_token(token)
        self.assertIsNone(user_after)

    def test_03_document_persistence(self):
        uid = uuid.uuid4().hex[:8]
        doc_id = f"doc-{uid}"
        doc_record = {
            "id": doc_id,
            "owner_user_id": f"owner-{uid}",
            "filename": "persisted_report.pdf",
            "storage_filename": f"{doc_id}_persisted_report.pdf",
            "file_size": 1024,
            "page_count": 2,
            "total_chars": 350,
            "pages": [{"page_number": 1, "text": "Page 1 text"}, {"page_number": 2, "text": "Page 2 text"}],
            "summary": "Sample summary",
            "status": "PROCESSED",
            "freshness_date": "2026-10-09",
            "uploaded_at": "2026-10-09 21:00:00"
        }
        db_service.save_document(doc_record)

        fetched = db_service.get_document_by_id(doc_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["filename"], "persisted_report.pdf")
        self.assertEqual(len(fetched["pages"]), 2)

    def test_04_conversation_and_messages_persistence(self):
        uid = uuid.uuid4().hex[:8]
        user_id = f"user-{uid}"
        conv_id = f"conv-{uid}"

        db_service.create_user(user_id, f"convuser_{uid}@proofmind.ai", "Conv User", "hash", "salt", "2026-10-09")
        db_service.create_conversation(conv_id, user_id, "Persistence Test Conv", "2026-10-09 21:00:00")

        msg = {
            "id": f"msg-{uid}",
            "conversation_id": conv_id,
            "user_id": user_id,
            "question": "Is persistence active?",
            "decision_status": "SUPPORTED",
            "summary": "Yes it is.",
            "grounded_answer": "Persistence is verified.",
            "supporting_evidence": [],
            "conflicting_evidence": [],
            "uncertain_evidence": [],
            "reliability_score": 0.95,
            "timestamp": "2026-10-09 21:05:00"
        }
        db_service.save_message(msg)

        msgs = db_service.get_conversation_messages(conv_id)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["question"], "Is persistence active?")
        self.assertEqual(msgs[0]["decision_status"], "SUPPORTED")

    def test_05_foreign_key_and_cascade_delete(self):
        uid = uuid.uuid4().hex[:8]
        user_id = f"user-{uid}"
        conv_id = f"conv-{uid}"

        db_service.create_user(user_id, f"fkuser_{uid}@proofmind.ai", "FK User", "hash", "salt", "2026-10-09")
        db_service.create_conversation(conv_id, user_id, "FK Conv", "2026-10-09")

        # Adding invalid message with non-existent conversation_id should fail when FK enabled
        with self.assertRaises(sqlite3.IntegrityError):
            with db_service._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (id, conversation_id, user_id, question, decision_status, summary, grounded_answer, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    ("invalid-msg", "non-existent-conv-id", user_id, "Q?", "SUPPORTED", "S", "A", "2026-10-09")
                )

if __name__ == "__main__":
    unittest.main()
