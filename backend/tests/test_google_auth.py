import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.db_service import db_service

class TestGoogleAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @patch("app.services.auth_service.auth_service.verify_google_token")
    def test_01_google_auth_new_user_creation(self, mock_verify):
        mock_verify.return_value = {
            "sub": "google-sub-99901",
            "email": "google_new_user@example.com",
            "name": "Google New User",
            "email_verified": True
        }

        res = self.client.post("/api/v1/auth/google", json={"token": "mock_google_id_token_1"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertEqual(data["user"]["email"], "google_new_user@example.com")
        self.assertEqual(data["user"]["full_name"], "Google New User")
        self.assertTrue(data["token"].startswith("pm_token_"))

        # Verify record exists in SQLite with google_sub
        db_user = db_service.get_user_by_google_sub("google-sub-99901")
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user["email"], "google_new_user@example.com")

    @patch("app.services.auth_service.auth_service.verify_google_token")
    def test_02_google_auth_existing_user_login(self, mock_verify):
        mock_verify.return_value = {
            "sub": "google-sub-99901",
            "email": "google_new_user@example.com",
            "name": "Google New User",
            "email_verified": True
        }

        res = self.client.post("/api/v1/auth/google", json={"token": "mock_google_id_token_2"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user"]["email"], "google_new_user@example.com")

    def test_03_invalid_google_token_rejection(self):
        res = self.client.post("/api/v1/auth/google", json={"token": "invalid_fake_google_token_xyz"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("detail", res.json())

    @patch("app.services.auth_service.auth_service.verify_google_token")
    def test_04_session_and_logout(self, mock_verify):
        mock_verify.return_value = {
            "sub": "google-sub-99902",
            "email": "google_session_user@example.com",
            "name": "Session User",
            "email_verified": True
        }

        res_login = self.client.post("/api/v1/auth/google", json={"token": "mock_token"})
        token = res_login.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check me
        res_me = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)

        # Logout
        res_logout = self.client.post("/api/v1/auth/logout", headers=headers)
        self.assertEqual(res_logout.status_code, 200)

        # Me should now fail
        res_me_after = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res_me_after.status_code, 401)

if __name__ == "__main__":
    unittest.main()
