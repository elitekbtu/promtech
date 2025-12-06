# Backend Technical Documentation — PromTech API (FastAPI + Gemini + Face ID)

## 1. Project Overview

**PromTech Backend** (currently labeled as "Zamanbank API" in code) — FastAPI-based backend service with AI-powered features including:

- User authentication and registration with email/phone
- Face ID verification using DeepFace and Facenet512
- Agentic RAG system powered by LangGraph and Google Gemini
- Role-based access control (admin/user)
- RESTful API endpoints
- Integration with vector databases (FAISS, ChromaDB) for semantic search
- Web search integration via Tavily

---

## 2. Technology Stack

### 2.1 Core Framework

- **FastAPI** 0.104+ — Modern async Python web framework
- **Uvicorn** — ASGI server
- **SQLAlchemy** — ORM for database operations
- **PostgreSQL** — Primary database (via psycopg2-binary)
- **Pydantic** 2.5+ — Data validation

### 2.2 AI & ML Components

- **Google Gemini** (via langchain-google-genai, google-generativeai) — Primary LLM
- **LangChain** 0.1+ — LLM framework
- **LangGraph** 0.0.20+ — Multi-agent orchestration
- **DeepFace** — Face recognition library
- **TensorFlow** 2.0+ / tf-keras — Deep learning backend
- **Facenet512** model (via DeepFace)
- **RetinaFace** — Face detection backend

### 2.3 Vector & Search

- **FAISS** (faiss-cpu 1.7.4+) — Vector similarity search
- **ChromaDB** 0.4+ — Vector database
- **Tavily** 0.3+ — Web search API
- **rank-bm25** 0.2.2+ — BM25 ranking algorithm

### 2.4 Supporting Libraries

- **python-dotenv** — Environment variable management
- **passlib[bcrypt]** & **bcrypt** 4.0.1 — Password hashing
- **python-multipart** — File upload support
- **email-validator** — Email validation
- **Pillow** — Image processing
- **OpenCV** (opencv-python) — Computer vision
- **PyPDF** 6.0+ — PDF processing

---

## 3. System Architecture

### 3.1 Project Structure

```text
backend/
├── main.py                 # FastAPI application entry point
├── database.py             # SQLAlchemy configuration & session
├── requirements.txt        # Python dependencies
│
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py
│   └── user.py            # User model
│
├── services/              # Business logic modules
│   ├── __init__.py
│   └── auth/              # Authentication module
│       ├── router.py      # Auth API endpoints
│       ├── schemas.py     # Pydantic request/response models
│       └── service.py     # Auth business logic
│
├── faceid/                # Face ID verification module
│   ├── __init__.py
│   ├── router.py          # Face verification endpoints
│   ├── schemas.py         # Face ID response models
│   └── service.py         # DeepFace integration & matching
│
└── rag_agent/             # Agentic RAG system
    ├── config/            # RAG configuration
    │   ├── __init__.py
    │   ├── langchain.py   # LangChain LLM setup
    │   ├── langraph.py    # LangGraph agent definitions
    │   └── orchestrator.py # Agent orchestration logic
    │
    ├── routes/            # RAG API endpoints
    │   ├── __init__.py
    │   ├── router.py      # Standard RAG queries
    │   └── live_query_router.py # Live/streaming queries
    │
    ├── schemas/           # RAG request/response models
    │   ├── __init__.py
    │   └── schemas.py
    │
    ├── tools/             # Agent tools
    │   ├── __init__.py
    │   ├── vector_search.py  # Vector DB search
    │   └── web_search.py     # Tavily web search
    │
    ├── utils/             # Utility functions
    │   ├── __init__.py
    │   └── vector_store.py   # Vector store management
    │
    └── scripts/           # Initialization & setup
        └── initialize_vector_db.py
```

### 3.2 Application Initialization

From `main.py`:

```python
app = FastAPI(title="Zamanbank API", version="1.0.0")

# CORS middleware for cross-origin requests
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

# Route registration
app.include_router(auth_router, prefix="/api/auth")
app.include_router(faceid_router, prefix="/api/faceid", tags=["Face Verification"])
app.include_router(rag_router, tags=["RAG"])
app.include_router(rag_live_query_router, tags=["RAG Live Query"])

# Database initialization
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
```

### 3.3 Core Components

#### 3.3.1 Database Layer (`database.py`)

- SQLAlchemy engine with PostgreSQL
- Session management with `SessionLocal`
- Declarative base for ORM models
- Dependency injection via `get_db()`

#### 3.3.2 Authentication Module (`services/auth/`)

**Endpoints:**

- `POST /api/auth/register` — User registration with optional avatar
- `POST /api/auth/login` — Email/password login
- `PUT /api/auth/{user_id}/avatar` — Update user avatar

**Features:**

- Email/password validation
- Password hashing with bcrypt
- Avatar file upload support
- User role management (admin/user)

#### 3.3.3 Face ID Module (`faceid/`)

**Endpoints:**

- `POST /api/faceid/verify` — Verify face against all registered users

**Service Configuration:**

- Model: **Facenet512** (512-dimensional face embeddings)
- Detector: **RetinaFace** (robust face detection)
- Distance Metric: **Cosine** similarity
- Matches uploaded image against all user avatars in database
- Returns matched user with confidence score

#### 3.3.4 RAG Agent Module (`rag_agent/`)

**Architecture:**

- **Orchestrator** coordinates between LangChain and LangGraph
- **Supervisor Agent** routes queries to specialist agents
- **Specialist Agents** handle specific query types
- **Tools**: Vector search, web search
- **Vector Stores**: FAISS and ChromaDB support

**Endpoints:**

- `POST /api/rag/query` — Process RAG queries
- Additional live query endpoints for streaming

**Configuration:**

- Default LLM: Google Gemini
- Supports parallel agent execution
- Max 5 agent iterations
- Includes source citations and confidence scores

---

## 4. Data Models

### 4.1 User Model

Located in `models/user.py`:

| Field         | Type     | Description                      |
| ------------- | -------- | -------------------------------- |
| id            | Integer  | Primary key                      |
| name          | String   | User's first name (required)     |
| surname       | String   | User's last name (required)      |
| email         | String   | Unique email (required, indexed) |
| phone         | String   | Unique phone (required, indexed) |
| password_hash | String   | Bcrypt hashed password           |
| avatar        | String   | Avatar file path (optional)      |
| role          | String   | Role: "admin" or "user"          |
| created_at    | DateTime | Account creation timestamp       |
| updated_at    | DateTime | Last update timestamp            |
| deleted_at    | DateTime | Soft delete timestamp (nullable) |

**Notes:**

- Email and phone must be unique
- Avatar stored as file path for Face ID verification
- Supports soft deletion via `deleted_at` field

---

## 5. API Documentation

### 5.1 Authentication Endpoints

#### POST `/api/auth/register`

Register a new user with optional avatar for Face ID.

**Form Data:**

- `name` (required): First name (2-50 chars)
- `surname` (required): Last name (2-50 chars)
- `email` (required): Valid email format
- `phone` (required): Phone number (e.g., +77001234567)
- `password` (required): Password (8-72 chars)
- `avatar` (optional): Image file for face recognition

**Response:** `UserRead` schema with user details

**Validation:**

- Email format validation
- Password length requirements (8-72 characters)
- Name length validation (2-50 characters)

#### POST `/api/auth/login`

Login with email and password.

**Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `UserRead` schema with user information

**Status Codes:**

- 200: Success
- 401: Invalid credentials
- 422: Validation error

#### PUT `/api/auth/{user_id}/avatar`

Update user's avatar image.

**Form Data:**

- `avatar` (required): New image file

**Response:** Updated `UserRead`

---

### 5.2 Face ID Endpoints

#### POST `/api/faceid/verify`

Verify uploaded face against all registered users.

**Form Data:**

- `file` (required): Image file containing a face

**Response:**

```json
{
  "success": true,
  "verified": true,
  "message": "Face verified successfully! Welcome, John Doe",
  "user": {
    "user_id": 1,
    "name": "John",
    "surname": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "avatar": "user_1_avatar.jpg",
    "created_at": "2025-01-01T00:00:00"
  },
  "confidence": 0.95
}
```

**Flow:**

1. Receives image file from client (camera or upload)
2. DeepFace detects face in uploaded image
3. Extracts 512-dimensional face embedding (Facenet512)
4. Compares against all registered user avatars
5. Returns best match if confidence threshold met
6. Uses cosine distance for similarity matching

**Error Cases:**

- No face detected in image
- Multiple faces detected (ambiguous)
- No matching user found
- Face quality too low

---

### 5.3 RAG Endpoints

#### POST `/api/rag/query`

Process a query through the RAG system.

**Request:**

```json
{
  "query": "What are the benefits of using LangGraph?",
  "context": {
    "user_id": "123",
    "session_id": "abc"
  },
  "environment": "development"
}
```

**Response:**

```json
{
  "query": "What are the benefits of using LangGraph?",
  "response": "LangGraph provides several key benefits...",
  "sources": [
    {
      "type": "vector_search",
      "content": "...",
      "score": 0.92
    }
  ],
  "confidence": 0.88,
  "status": "success"
}
```

**RAG Flow:**

1. Query received by API endpoint
2. Orchestrator initializes RAG system if needed
3. Supervisor agent analyzes query intent
4. Routes to appropriate specialist agent
5. Agent uses tools (vector search, web search)
6. Gathers relevant context from sources
7. Gemini generates final response
8. Returns response with sources and confidence

---

## 6. Configuration

### 6.1 Environment Variables

Required in `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro
TAVILY_API_KEY=your-tavily-api-key  # Optional

# File Storage
FILE_STORAGE_PATH=/app/storage/avatars
FILE_STORAGE_BASE_URL=http://localhost:8000/storage
```

### 6.2 RAG System Configuration

From `rag_agent/config/orchestrator.py`:

```python
class OrchestratorConfig:
    default_llm_provider: str = "google"
    enable_parallel_agents: bool = True
    max_agent_iterations: int = 5
    include_sources: bool = True
    include_confidence_scores: bool = True
    max_response_length: int = 2000
```

### 6.3 Face ID Configuration

From `faceid/service.py`:

```python
FaceIDService(
    model_name="Facenet512",      # 512-dim embeddings
    detector_backend="retinaface", # Robust detection
    distance_metric="cosine"       # Similarity measure
)
```

---

## 7. Deployment

### 7.1 Docker Compose (Recommended)

1. Create `.env` file with required variables
2. Run:

```bash
docker-compose up --build
```

3. Access:
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### 7.2 Local Development

**Prerequisites:**

- Python 3.10+
- PostgreSQL 14+

**Setup:**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run migrations (if using Alembic)
alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7.3 Database Setup

```bash
# Create PostgreSQL database
createdb promtech_db

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/promtech_db

# Tables auto-created on startup via:
Base.metadata.create_all(bind=engine)
```

---

## 8. Request Flow Examples

### 8.1 User Registration with Face ID

```
Client → POST /api/auth/register
        ├─ Form: name, surname, email, phone, password, avatar
        ├─ Validate inputs
        ├─ Hash password with bcrypt
        ├─ Save avatar file to storage
        ├─ Create user in database
        └─ Return UserRead response
```

### 8.2 Face ID Verification

```
Client → POST /api/faceid/verify
        ├─ Upload face image
        ├─ DeepFace detects face
        ├─ Extract Facenet512 embeddings
        ├─ Query all user avatars from DB
        ├─ Compare with cosine distance
        ├─ Find best match above threshold
        └─ Return matched user + confidence
```

### 8.3 RAG Query Processing

```
Client → POST /api/rag/query
        ├─ Initialize orchestrator
        ├─ Supervisor agent analyzes intent
        ├─ Route to specialist agent
        │   ├─ Vector search tool → FAISS/ChromaDB
        │   ├─ Web search tool → Tavily API
        │   └─ Gather context from sources
        ├─ Gemini generates final response
        └─ Return answer + sources + confidence
```

---

## 9. Security Considerations

### 9.1 Password Security

- Bcrypt hashing with salt
- Minimum 8 characters, maximum 72 characters
- Passwords never stored in plain text

### 9.2 Face ID Security

- Avatars stored securely on server
- Face embeddings compared server-side
- No face data sent to client
- Cosine distance threshold prevents false positives

### 9.3 API Security

- CORS configured for cross-origin requests
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM
- File upload validation and sanitization

---

## 10. Future Improvements

### 10.1 Planned Features

- JWT token-based authentication (currently simple)
- Refresh token mechanism
- Rate limiting on API endpoints
- Enhanced logging and monitoring
- Database migrations with Alembic
- API versioning
- Caching layer (Redis)

### 10.2 RAG Enhancements

- Custom domain-specific tools
- Multi-language support
- Conversation history persistence
- Fine-tuned embedding models
- Hybrid search (vector + keyword)

### 10.3 Face ID Improvements

- Liveness detection
- Multi-face tracking
- Face quality scoring
- Age/expression invariance
- Privacy-preserving face embeddings

---

## 11. Troubleshooting

### 11.1 Common Issues

**Face verification fails:**

- Ensure good lighting in photos
- Face should be clearly visible
- Check avatar files are properly saved
- Verify DeepFace models downloaded

**RAG queries timeout:**

- Check Gemini API key validity
- Verify Tavily API key if using web search
- Increase `max_agent_iterations` if needed
- Check vector store initialization

**Database connection errors:**

- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists
- Check network connectivity

### 11.2 Logs & Debugging

Enable debug logging in development:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check FastAPI automatic docs for API testing:

- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 12. API Reference Summary

| Endpoint                         | Method | Description                  | Auth |
| -------------------------------- | ------ | ---------------------------- | ---- |
| `/api/health`                    | GET    | Health check                 | No   |
| `/api/auth/register`             | POST   | Register new user            | No   |
| `/api/auth/login`                | POST   | Login with email/password    | No   |
| `/api/auth/{user_id}/avatar`     | PUT    | Update user avatar           | Yes  |
| `/api/faceid/verify`             | POST   | Verify face against database | No   |
| `/api/rag/query`                 | POST   | Process RAG query            | No   |
| `/api/rag/live-query` (if exist) | POST   | Streaming RAG queries        | No   |

---

## 13. Development Notes

### 13.1 Code Organization

- **Modular structure** with clear separation of concerns
- Each module (auth, faceid, rag_agent) is self-contained
- Pydantic schemas for all API contracts
- SQLAlchemy models separate from API schemas
- Service layer for business logic

### 13.2 Testing Strategy

Recommended test structure (not yet implemented):

```
tests/
├── test_auth.py          # Auth endpoint tests
├── test_faceid.py        # Face verification tests
├── test_rag.py           # RAG system tests
├── test_models.py        # Database model tests
└── fixtures/             # Test data & mocks
```

### 13.3 Dependencies Management

Using `requirements.txt` for now. Consider migrating to:

- `pyproject.toml` with Poetry or PDM
- `uv` for faster dependency resolution
- Version pinning for production stability

---

This documentation reflects the **actual current state** of the backend implementation as of the latest code review.
