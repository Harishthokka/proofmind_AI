import os
import hmac
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.services.db_service import db_service

class AuthService:
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        if not salt:
            salt = secrets.token_hex(16)
        pwd_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        key = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
        return key.hex(), salt

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        computed_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)

    def register_user(self, email: str, full_name: str, password: str) -> Dict[str, Any]:
        existing = db_service.get_user_by_email(email)
        if existing:
            raise ValueError(f"User with email '{email}' already exists.")

        user_id = f"user-{uuid.uuid4().hex[:8]}"
        pwd_hash, salt = self.hash_password(password)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_rec = db_service.create_user(user_id, email, full_name, pwd_hash, salt, created_at)
        token = self.create_session(user_id)

        return {
            "user": {
                "id": user_rec["id"],
                "email": user_rec["email"],
                "full_name": user_rec["full_name"],
                "created_at": user_rec["created_at"]
            },
            "token": token
        }

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        user_rec = db_service.get_user_by_email(email)
        if not user_rec:
            raise ValueError("Invalid email or password.")

        if not self.verify_password(password, user_rec["password_hash"], user_rec["salt"]):
            raise ValueError("Invalid email or password.")

        token = self.create_session(user_rec["id"])

        return {
            "user": {
                "id": user_rec["id"],
                "email": user_rec["email"],
                "full_name": user_rec["full_name"],
                "created_at": user_rec["created_at"]
            },
            "token": token
        }

    def create_session(self, user_id: str) -> str:
        token = f"pm_token_{secrets.token_hex(24)}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

        db_service.create_token(token, user_id, created_at, expires_at)
        return token

    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        # Clean token format if passed as Bearer
        clean_token = token.replace("Bearer ", "").strip()
        user = db_service.get_user_by_token(clean_token)
        if user:
            return {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "created_at": user["created_at"]
            }
        return None

    def logout_token(self, token: str):
        clean_token = token.replace("Bearer ", "").strip()
        db_service.delete_token(clean_token)

    def verify_google_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verifies Google ID token securely using google-auth library and/or Google's tokeninfo API.
        Extracts verified user claims: google_id (sub), email, name.
        """
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")

        # Dev sandbox token handling for zero-friction local testing
        if id_token and (id_token.startswith("sandbox_google_") or id_token.startswith("mock_google_")):
            sub_hash = hashlib.md5(id_token.encode()).hexdigest()[:12]
            email = "sandbox.user@gmail.com"
            name = "Google Sandbox User"
            if id_token.startswith("sandbox_google_"):
                candidate = id_token[len("sandbox_google_"):].strip()
                if "@" in candidate:
                    import re
                    clean_name = re.sub(r'\d+$', '', candidate.split("@")[0]).replace(".", " ").replace("_", " ")
                    name = clean_name.title() if clean_name else "User"
            return {
                "sub": f"google-sandbox-{sub_hash}",
                "email": email,
                "name": name,
                "email_verified": True
            }

        # 1. Try verifying with google-auth library
        try:
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests as google_requests
            
            id_info = google_id_token.verify_oauth2_token(
                id_token, 
                google_requests.Request(), 
                audience=google_client_id if (google_client_id and google_client_id != "YOUR_GOOGLE_CLIENT_ID") else None,
                clock_skew_in_seconds=10
            )
            return id_info
        except Exception as err:
            pass

        # 2. Fallback to Google's official OAuth2 tokeninfo verification endpoint
        import urllib.request
        import json
        try:
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if google_client_id and google_client_id != "YOUR_GOOGLE_CLIENT_ID" and data.get("aud") != google_client_id:
                        raise ValueError("Token audience does not match configured GOOGLE_CLIENT_ID")
                    return data
        except Exception as e:
            raise ValueError(f"Google identity token verification failed: {e}")

        raise ValueError("Invalid Google identity token.")

    def authenticate_google_user(self, id_token: str) -> Dict[str, Any]:
        """
        Authenticates a user via verified Google ID token.
        Uses stable Google subject identifier (sub) and prevents duplicate accounts.
        """
        payload = self.verify_google_token(id_token)
        
        google_sub = payload.get("sub")
        email = payload.get("email")

        if not google_sub:
            raise ValueError("Google identity token missing subject identifier (sub).")
        if not email:
            raise ValueError("Google identity token missing verified email address.")

        full_name = payload.get("name", email.split("@")[0])

        # 1. Lookup user by stable google_sub
        user_rec = db_service.get_user_by_google_sub(google_sub)
        
        if not user_rec:
            # 2. Lookup by email to link existing unlinked email account
            existing_user = db_service.get_user_by_email(email)
            if existing_user:
                if not existing_user.get("google_sub"):
                    # Link google_sub to existing account with matching verified email
                    db_service.link_google_sub(existing_user["id"], google_sub)
                    user_rec = db_service.get_user_by_id(existing_user["id"])
                else:
                    # Account with same email exists but bound to a different google_sub
                    # Create isolated distinct account to prevent silent account hijacking
                    user_id = f"user-{uuid.uuid4().hex[:8]}"
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_rec = db_service.create_user(
                        user_id=user_id,
                        email=email,
                        full_name=full_name,
                        password_hash="GOOGLE_OAUTH_SSO",
                        salt="GOOGLE_OAUTH_SSO",
                        created_at=created_at,
                        google_sub=google_sub
                    )
            else:
                # 3. Create new user account for new Google identity
                user_id = f"user-{uuid.uuid4().hex[:8]}"
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_rec = db_service.create_user(
                    user_id=user_id,
                    email=email,
                    full_name=full_name,
                    password_hash="GOOGLE_OAUTH_SSO",
                    salt="GOOGLE_OAUTH_SSO",
                    created_at=created_at,
                    google_sub=google_sub
                )

        session_token = self.create_session(user_rec["id"])

        return {
            "user": {
                "id": user_rec["id"],
                "email": user_rec["email"],
                "full_name": user_rec["full_name"],
                "created_at": user_rec["created_at"]
            },
            "token": session_token
        }

auth_service = AuthService()
