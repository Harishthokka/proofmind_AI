import os
import json
import sqlite3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Storage directory for SQLite database
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "proofmind.db")

class DatabaseService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes SQLite database tables for users, tokens, documents, conversations, and messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    google_sub TEXT
                );
            """)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN google_sub TEXT;")
            except Exception:
                pass

            # 2. Auth Tokens Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
            """)

            # 3. User Documents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    storage_filename TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    page_count INTEGER NOT NULL,
                    total_chars INTEGER NOT NULL,
                    pages_json TEXT NOT NULL,
                    summary TEXT,
                    status TEXT NOT NULL,
                    freshness_date TEXT,
                    uploaded_at TEXT NOT NULL
                );
            """)

            # 4. Conversations Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
            """)

            # 5. Conversation Documents Mapping Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_documents (
                    conversation_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    PRIMARY KEY (conversation_id, document_id)
                );
            """)

            # 6. Messages / Analyses Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    decision_status TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    grounded_answer TEXT NOT NULL,
                    supporting_evidence_json TEXT,
                    conflicting_evidence_json TEXT,
                    uncertain_evidence_json TEXT,
                    missing_information TEXT,
                    suggested_doc_request TEXT,
                    citation_verification_summary TEXT,
                    abstention_explanation TEXT,
                    freshness_rating TEXT,
                    date_precedence_note TEXT,
                    reliability_score REAL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
                );
            """)

            conn.commit()
            logger.info("ProofMind AI SQLite Database initialized successfully.")

    # --- User & Auth Methods ---
    def create_user(self, user_id: str, email: str, full_name: str, password_hash: str, salt: str, created_at: str, google_sub: Optional[str] = None) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, email, full_name, password_hash, salt, created_at, google_sub) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, email.lower().strip(), full_name.strip(), password_hash, salt, created_at, google_sub)
            )
            conn.commit()
        return {"id": user_id, "email": email, "full_name": full_name, "created_at": created_at, "google_sub": google_sub}

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.lower().strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_google_sub(self, google_sub: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE google_sub = ?", (google_sub,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def link_google_sub(self, user_id: str, google_sub: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET google_sub = ? WHERE id = ?", (google_sub, user_id))
            conn.commit()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_token(self, token: str, user_id: str, created_at: str, expires_at: Optional[str] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tokens (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (token, user_id, created_at, expires_at)
            )
            conn.commit()

    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.* FROM users u
                JOIN tokens t ON u.id = t.user_id
                WHERE t.token = ?
            """, (token,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_token(self, token: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tokens WHERE token = ?", (token,))
            conn.commit()

    # --- Document Management Methods ---
    def save_document(self, doc_data: Dict[str, Any]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (id, owner_user_id, filename, storage_filename, file_size, page_count, total_chars, pages_json, summary, status, freshness_date, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_data["id"],
                doc_data.get("owner_user_id", "demo-user-id"),
                doc_data["filename"],
                doc_data.get("storage_filename", doc_data["filename"]),
                doc_data["file_size"],
                doc_data["page_count"],
                doc_data.get("total_chars", 0),
                json.dumps(doc_data.get("pages", [])),
                doc_data.get("summary", ""),
                doc_data.get("status", "PROCESSED"),
                doc_data.get("freshness_date", ""),
                doc_data["uploaded_at"]
            ))
            conn.commit()

    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE owner_user_id = ? ORDER BY uploaded_at DESC", (user_id,))
            rows = cursor.fetchall()
            docs = []
            for r in rows:
                d = dict(r)
                d["pages"] = json.loads(d["pages_json"])
                docs.append(d)
            return docs

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["pages"] = json.loads(d["pages_json"])
                return d
            return None

    def delete_document(self, doc_id: str, user_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ? AND owner_user_id = ?", (doc_id, user_id))
            deleted = cursor.rowcount > 0
            if deleted:
                cursor.execute("DELETE FROM conversation_documents WHERE document_id = ?", (doc_id,))
            conn.commit()
            return deleted

    # --- Conversation & Message Methods ---
    def create_conversation(self, conv_id: str, user_id: str, title: str, created_at: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (conv_id, user_id, title, created_at, created_at)
            )
            conn.commit()
        return {"id": conv_id, "user_id": user_id, "title": title, "created_at": created_at, "updated_at": created_at}

    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_conversation_by_id(self, conv_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE id = ? AND user_id = ?", (conv_id, user_id))
            row = cursor.fetchone()
            return dict(row) if row else None

    def link_document_to_conversation(self, conv_id: str, doc_id: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO conversation_documents (conversation_id, document_id) VALUES (?, ?)", (conv_id, doc_id))
            conn.commit()

    def get_conversation_documents(self, conv_id: str) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT document_id FROM conversation_documents WHERE conversation_id = ?", (conv_id,))
            return [row["document_id"] for row in cursor.fetchall()]

    def save_message(self, msg_data: Dict[str, Any]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Ensure conversation exists to satisfy foreign key
            cursor.execute("SELECT id FROM conversations WHERE id = ?", (msg_data["conversation_id"],))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO conversations (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (msg_data["conversation_id"], msg_data["user_id"], "Analysis Workspace", msg_data["timestamp"], msg_data["timestamp"])
                )
            cursor.execute("""
                INSERT OR REPLACE INTO messages 
                (id, conversation_id, user_id, question, decision_status, summary, grounded_answer,
                 supporting_evidence_json, conflicting_evidence_json, uncertain_evidence_json,
                 missing_information, suggested_doc_request, citation_verification_summary,
                 abstention_explanation, freshness_rating, date_precedence_note, reliability_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                msg_data["id"],
                msg_data["conversation_id"],
                msg_data["user_id"],
                msg_data["question"],
                msg_data["decision_status"],
                msg_data["summary"],
                msg_data["grounded_answer"],
                json.dumps([e.model_dump() if hasattr(e, "model_dump") else e for e in msg_data.get("supporting_evidence", [])]),
                json.dumps([e.model_dump() if hasattr(e, "model_dump") else e for e in msg_data.get("conflicting_evidence", [])]),
                json.dumps([e.model_dump() if hasattr(e, "model_dump") else e for e in msg_data.get("uncertain_evidence", [])]),
                msg_data.get("missing_information"),
                msg_data.get("suggested_doc_request"),
                msg_data.get("citation_verification_summary", ""),
                msg_data.get("abstention_explanation"),
                msg_data.get("freshness_rating", "CURRENT"),
                msg_data.get("date_precedence_note"),
                msg_data.get("reliability_score", 0.0),
                msg_data["timestamp"]
            ))
            cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (msg_data["timestamp"], msg_data["conversation_id"]))
            conn.commit()

    def get_conversation_messages(self, conv_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conv_id,))
            rows = cursor.fetchall()
            msgs = []
            for r in rows:
                m = dict(r)
                m["supporting_evidence"] = json.loads(m["supporting_evidence_json"] or "[]")
                m["conflicting_evidence"] = json.loads(m["conflicting_evidence_json"] or "[]")
                m["uncertain_evidence"] = json.loads(m["uncertain_evidence_json"] or "[]")
                msgs.append(m)
            return msgs

    def get_user_messages(self, user_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
            rows = cursor.fetchall()
            msgs = []
            for r in rows:
                m = dict(r)
                m["supporting_evidence"] = json.loads(m["supporting_evidence_json"] or "[]")
                m["conflicting_evidence"] = json.loads(m["conflicting_evidence_json"] or "[]")
                m["uncertain_evidence"] = json.loads(m["uncertain_evidence_json"] or "[]")
                msgs.append(m)
            return msgs

    def get_message_by_id(self, msg_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
            row = cursor.fetchone()
            if row:
                m = dict(row)
                m["supporting_evidence"] = json.loads(m["supporting_evidence_json"] or "[]")
                m["conflicting_evidence"] = json.loads(m["conflicting_evidence_json"] or "[]")
                m["uncertain_evidence"] = json.loads(m["uncertain_evidence_json"] or "[]")
                return m
            return None

    def update_document(self, doc_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            allowed_fields = {
                "filename": "filename",
                "content_summary": "summary",
                "summary": "summary",
                "freshness_date": "freshness_date"
            }
            clauses = []
            values = []
            for k, val in updates.items():
                if k in allowed_fields and val is not None:
                    db_col = allowed_fields[k]
                    clauses.append(f"{db_col} = ?")
                    values.append(val)
            if not clauses:
                return self.get_document_by_id(doc_id)
            values.extend([doc_id, user_id])
            cursor.execute(f"UPDATE documents SET {', '.join(clauses)} WHERE id = ? AND owner_user_id = ?", values)
            conn.commit()
            return self.get_document_by_id(doc_id)

    def update_message(self, msg_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            allowed_fields = {
                "grounded_answer": "grounded_answer",
                "summary": "summary",
                "question": "question",
                "decision_status": "decision_status"
            }
            clauses = []
            values = []
            for k, val in updates.items():
                if k in allowed_fields and val is not None:
                    db_col = allowed_fields[k]
                    val_str = val.value if hasattr(val, "value") else str(val)
                    clauses.append(f"{db_col} = ?")
                    values.append(val_str)
            if not clauses:
                return self.get_message_by_id(msg_id)
            values.extend([msg_id, user_id])
            cursor.execute(f"UPDATE messages SET {', '.join(clauses)} WHERE id = ? AND user_id = ?", values)
            conn.commit()
            return self.get_message_by_id(msg_id)

db_service = DatabaseService()

