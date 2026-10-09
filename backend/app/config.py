import os
from typing import List

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ProofMind AI API")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
        ).split(",")
        if origin.strip()
    ]
    CORS_ORIGIN_REGEX: str = os.getenv(
        "CORS_ORIGIN_REGEX",
        r"https:\/\/.*\.vercel\.app|https:\/\/.*\.onrender\.com"
    )
    STATIC_DIR: str = os.getenv("STATIC_DIR", "")

settings = Settings()
