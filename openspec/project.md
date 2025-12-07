# Project Context

## Purpose

**PromTech** is a full-stack application featuring AI-powered capabilities including:

- User authentication with face ID verification
- Agentic RAG (Retrieval-Augmented Generation) system for intelligent query processing
- Real-time chat interface with Google Gemini integration
- Multi-modal AI interactions (text, voice, screen capture)

**Current State:** The project is labeled as "Zamanbank API" in code but is being developed as PromTech. The backend has modular architecture with authentication, face recognition, and RAG capabilities.

## Tech Stack

### Backend

- **FastAPI** 0.104+ — Modern async Python web framework
- **Python 3.10+** — Core language
- **SQLAlchemy** — ORM for database operations
- **PostgreSQL 15** — Primary database (via psycopg2-binary)
- **Pydantic** 2.5+ — Data validation and schemas

### AI & Machine Learning

- **Google Gemini** (via langchain-google-genai) — Primary LLM
- **LangChain** 0.1+ — LLM application framework
- **LangGraph** 0.0.20+ — Multi-agent orchestration system
- **DeepFace** — Face recognition (Facenet512 model, RetinaFace detector)
- **TensorFlow** 2.0+ / tf-keras — Deep learning backend
- **FAISS** (faiss-cpu 1.7.4+) — Vector similarity search
- **ChromaDB** 0.4+ — Vector database
- **Tavily** 0.3+ — Web search API integration

### Frontend

- **Expo** ~54.0 — React Native framework
- **React Native** 0.81.4 — Mobile/web cross-platform
- **React** 19.1.0 — UI library
- **TypeScript** 5.9+ — Type-safe JavaScript
- **Expo Router** 6.0+ — File-based routing
- **Zustand** 5.0+ — State management
- **React Native Reanimated** 4.1+ — Animations
- **Expo Camera** 16.0+ — Camera access for Face ID

### Infrastructure

- **Docker** & **Docker Compose** — Containerization
- **Uvicorn** — ASGI server
- **PostgreSQL** — Relational database
- **Git** — Version control

### Supporting Libraries

- **passlib[bcrypt]** & **bcrypt** 4.0.1 — Password hashing
- **python-multipart** — File upload support
- **python-dotenv** — Environment variable management
- **Pillow** — Image processing
- **OpenCV** (opencv-python) — Computer vision
- **PyPDF** 6.0+ — PDF processing
- **rank-bm25** 0.2.2+ — BM25 ranking algorithm

## Project Conventions

### Code Style

**Backend (Python):**

- PEP 8 style guide for Python code
- Snake_case for variables, functions, and modules
- PascalCase for classes
- Type hints using Python 3.10+ syntax
- Pydantic models for all API request/response schemas
- Docstrings for public functions and classes
- Maximum line length: 88 characters (Black formatter standard)

**Frontend (TypeScript/React Native):**

- ESLint with expo configuration
- camelCase for variables and functions
- PascalCase for components and types
- Functional components with hooks (no class components)
- TypeScript strict mode enabled
- File naming: kebab-case for files, PascalCase for component files

### Architecture Patterns

**Backend:**

- **Modular Monolith** architecture with feature-based organization
- Separation into distinct modules: `auth`, `faceid`, `rag_agent`
- **Service Layer Pattern**: Business logic in service files, routers only handle HTTP
- **Dependency Injection**: Database sessions via FastAPI dependencies
- **ORM Pattern**: SQLAlchemy models separate from Pydantic schemas
- **Repository Pattern** (implicit): Database access through SQLAlchemy ORM

**Structure:**

```
backend/
├── main.py              # FastAPI app entry point
├── database.py          # SQLAlchemy configuration
├── models/              # ORM models
├── services/            # Business logic modules
│   └── auth/           # Feature: router, service, schemas
├── faceid/             # Feature: Face ID verification
└── rag_agent/          # Feature: Agentic RAG
    ├── config/         # LangChain/LangGraph setup
    ├── routes/         # API endpoints
    ├── tools/          # Agent tools
    └── utils/          # Utilities
```

**Frontend:**

- **File-based routing** with Expo Router
- **Context API** for cross-cutting concerns (LiveAPIContext)
- **Custom hooks** for business logic (use-live-api.ts, use-rag-tools.ts)
- **Component composition** with reusable UI components
- **Separation of concerns**: API client, audio processing, UI components

**RAG System:**

- **Agentic architecture** using LangGraph
- **Orchestrator pattern**: Coordinates supervisor and specialist agents
- **Tool-based agents**: Vector search, web search tools
- **Multi-provider support**: Configurable LLM providers (Google Gemini primary)

### Testing Strategy

**Current State:** Testing infrastructure not yet implemented.

**Recommended Approach:**

- **Backend**: pytest with FastAPI TestClient
  - Unit tests for services
  - Integration tests for API endpoints
  - Mock external dependencies (Gemini, Tavily)
- **Frontend**: Jest + React Native Testing Library
  - Component tests
  - Hook tests
  - Integration tests for screens
- **E2E**: Detox or Expo's testing tools
- **CI/CD**: GitHub Actions for automated testing

### Git Workflow

**Branch Strategy:**

- `main` — Production-ready code
- Feature branches from `main`
- Commit message format: Conventional Commits (recommended)
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `refactor:` for code refactoring
  - `test:` for tests

**Deployment:**

- Docker Compose for local development
- Environment variables via `.env` file (see `env.example`)

## Domain Context

### Face ID Verification

- **DeepFace** library with **Facenet512** model (512-dimensional embeddings)
- **RetinaFace** detector for robust face detection
- **Cosine similarity** for face matching
- Flow: Capture → Detect → Extract embeddings → Compare → Match
- Threshold-based verification with confidence scores

### Agentic RAG System

- **Supervisor Agent**: Routes queries to appropriate specialist agents
- **Specialist Agents**: Handle specific query types
- **Tools**: Vector search (FAISS/ChromaDB), web search (Tavily)
- **Orchestrator**: Manages agent lifecycle and tool execution
- **Context Management**: Maintains conversation history and sources
- **Confidence Scoring**: Provides reliability metrics for responses

### Authentication

- Email/password based authentication
- Password hashing with bcrypt
- Role-based access control: `admin` vs `user`
- Avatar upload for Face ID enrollment
- Soft deletion support (deleted_at field)

### Multi-modal AI Interactions

- **Text chat**: Standard query-response
- **Live audio**: Real-time voice interaction with Gemini
- **Screen capture**: Context-aware AI with screen sharing
- **Webcam**: Visual context for AI queries

## Important Constraints

### Technical

- **Python 3.10+** required for backend
- **Node.js 18+** recommended for frontend
- **PostgreSQL 14+** required
- **Docker & Docker Compose** for deployment
- Face ID requires good lighting and clear face visibility
- RAG system requires API keys: `GEMINI_API_KEY`, `TAVILY_API_KEY`

### Performance

- Face verification processes all user avatars (scales linearly with users)
- Vector search performance depends on FAISS/ChromaDB index size
- Max agent iterations: 5 (configurable in orchestrator)
- Max response length: 2000 characters

### Security

- Passwords: 8-72 characters (bcrypt limitation)
- Face embeddings stored server-side only
- CORS enabled for all origins (development mode)
- **JWT Authentication**: Implemented with 7-day token expiration
  - Token-based authentication with Bearer scheme
  - Role-based access control (guest/expert roles)
  - Tokens include user_id, email, and role claims
  - Secret key configured via `SECRET_KEY` environment variable

### Business/Domain

- Currently branded as "Zamanbank API" but transitioning to PromTech
- Face ID designed for 1:N matching (one face against all users)
- RAG system includes source citations and confidence scores

## External Dependencies

### Required Services

- **Google Gemini API** — Primary LLM for chat and RAG
  - Requires: `GEMINI_API_KEY`, `GEMINI_MODEL`
  - Used for: Query processing, response generation, intent classification
- **Tavily API** (Optional) — Web search integration
  - Requires: `TAVILY_API_KEY`
  - Used for: Real-time web search in RAG system
- **PostgreSQL Database** — Data persistence
  - Requires: `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  - Managed via Docker Compose

### Python Package Dependencies

- Deep learning models downloaded on first run:
  - Facenet512 model (DeepFace)
  - RetinaFace detector weights
  - TensorFlow backend models

### Frontend Dependencies

- **Expo SDK** — Mobile development framework
- **Google Gemini API** — Direct client-side integration
- Camera permissions required for Face ID features

### Development Tools

- **Docker** — Containerization
- **Docker Compose** — Multi-container orchestration
- **.env file** — Environment configuration (see `env.example`)

### API Endpoints Summary

- `POST /api/auth/register` — User registration with avatar
- `POST /api/auth/login` — Email/password login
- `POST /api/faceid/verify` — Face verification
- `POST /api/rag/query` — RAG query processing
- `GET /api/health` — Health check

### File Storage

- User avatars stored locally in backend
- Path configurable via `FILE_STORAGE_PATH` and `FILE_STORAGE_BASE_URL`
- S3-compatible storage can be integrated later

### Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- Auto-generated from FastAPI/Pydantic schemas
