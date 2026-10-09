from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, documents, analysis, auth, conversations

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for ProofMind AI - Evidence-Aware AI Decision Support Engine",
    version="1.0.0"
)

# Configure CORS for local frontend & dev tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(analysis.router)
app.include_router(conversations.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to ProofMind AI API",
        "tagline": "Every decision needs evidence.",
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
