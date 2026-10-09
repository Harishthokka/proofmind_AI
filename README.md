# ProofMind AI — Evidence-Aware AI Decision Engine

> **"Every decision needs evidence."**  
> *Hackathon Problem Statement: PS-01*

ProofMind AI is an evidence-aware decision-support platform designed to analyze multi-document context, evaluate source freshness, detect conflicting claims, verify citation validity, and output decision-backed ratings (`SUPPORTED`, `NEEDS_VERIFICATION`, `INSUFFICIENT_EVIDENCE`).

---

## 🏗️ Phase 1 System Architecture

The project maintains clean separation between frontend and backend:

```
proofmind/
├── backend/                  # Python & FastAPI Service
│   ├── app/
│   │   ├── config.py         # CORS & Environment Config
│   │   ├── main.py           # FastAPI application root & middleware
│   │   ├── schemas/          # Pydantic schemas (Document & Analysis)
│   │   │   ├── document.py
│   │   │   └── analysis.py
│   │   ├── services/         # Modular Reasoning Services
│   │   │   ├── pdf_service.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── contradiction_service.py
│   │   │   ├── freshness_service.py
│   │   │   └── decision_service.py
│   │   └── routers/          # API Routers
│   │       ├── health.py     # /api/v1/health
│   │       ├── documents.py  # /api/v1/documents
│   │       └── analysis.py   # /api/v1/analysis
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/                 # React + Vite + Tailwind CSS SaaS Dashboard
│   ├── src/
│   │   ├── components/       # Reusable UI (Navbar, Sidebar, Badges, Cards)
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   ├── SummaryCard.jsx
│   │   │   ├── EvidenceCard.jsx
│   │   │   └── EmptyState.jsx
│   │   ├── pages/            # 4 Core Dashboard Pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DocumentAnalysis.jsx
│   │   │   ├── EvidenceExplorer.jsx
│   │   │   └── AnalysisHistory.jsx
│   │   ├── services/
│   │   │   └── api.js        # REST API integration
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css         # Glassmorphism dark SaaS visual theme
│   ├── .env.example
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── README.md
```

---

## ⚡ Quick Start & Run Instructions

### 1. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# (Optional) Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment example
cp .env.example .env

# Run FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 2. Frontend Setup (React + Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment example
cp .env.example .env

# Start development server
npm run dev
```
- **Frontend App**: [http://localhost:5173](http://localhost:5173)

---

## 🚦 Decision Status Model

ProofMind AI enforces 3 explicit decision outcomes based on evidence coverage:

| Status | Color | Description |
| :--- | :--- | :--- |
| `SUPPORTED` | Emerald Green | High confidence with verified supporting citations and zero unresolved contradictions. |
| `NEEDS_VERIFICATION` | Amber Orange | Supporting passages exist, but conflicting statements or dates require user verification. |
| `INSUFFICIENT_EVIDENCE` | Rose Crimson | No direct matching passage found in active document context to substantiate claim. |

---

## 📋 Features Delivered in Phase 1

- ✅ **Vite + React + Tailwind CSS Dashboard**: Dark navy glassmorphism SaaS UI (`#0B0F19`).
- ✅ **4 Complete Views**: Dashboard, Document Analysis, Evidence Explorer, Analysis History.
- ✅ **FastAPI Backend Core**: Clean modular architecture with Pydantic v2 schemas and CORS.
- ✅ **PDF Processing Service**: Page extraction, chunking, and text analysis pipeline.
- ✅ **Evidence Retrieval & Contradiction Engine**: Service abstractions for matching passages and identifying conflicting statements.
- ✅ **Freshness Assessment Engine**: Timeliness evaluation and rating (`CURRENT`, `OUTDATED`, `UNCERTAIN`).
- ✅ **Decision Synthesis**: Automatic status assignment (`SUPPORTED`, `NEEDS_VERIFICATION`, `INSUFFICIENT_EVIDENCE`).
- ✅ **API Health & Resilience**: Real REST API integration with reactive local fallback modes.

---

## 🔮 Next Recommended Phase (Phase 2)

1. **LLM RAG & Hybrid Vector Search**: Integrate local embeddings or vector indices (Faiss/ChromaDB).
2. **Deep Semantic Contradiction Detection**: NLI cross-encoder models for fine-grained claim conflict checking.
3. **PDF Highlighting & Bounding Box Viewer**: Visual PDF viewer inline with source passage citations.
