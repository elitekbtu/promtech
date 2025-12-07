# GidroAtlas - Water Resource Management System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.124.0-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![React Native](https://img.shields.io/badge/React_Native-Expo-blue.svg)](https://expo.dev/)

GidroAtlas is a full-stack water resource and hydrotechnical structures management system for Kazakhstan, featuring passport management, priority-based inspection scheduling, AI-powered RAG (Retrieval-Augmented Generation), and a native mobile application.

## 🌊 Features

### Water Object Management

- **Complete object database**: Lakes, reservoirs, canals, rivers, and hydraulic structures
- **Geographic information**: Coordinates, regions, administrative districts
- **Technical characteristics**: Dimensions, depths, water types, fauna classification
- **Passport management**: Upload, extract, and store technical passports (PDF)

### Priority-Based Inspection System

- **Automated priority calculation**: Based on technical condition and passport age
- **Priority levels**: HIGH (≥10), MEDIUM (6-9), LOW (≤5)
- **Formula**: `priority = (6 - technical_condition) * 3 + passport_age_years`
- **Expert dashboard**: Sortable priority table with filtering capabilities

### Role-Based Access Control

- **Guest role**: View water objects (priority fields hidden)
- **Expert role**: Full access including priorities, statistics, and management features
- **JWT authentication**: Secure token-based authentication with expo-secure-store

### AI-Powered RAG System

- **Intelligent queries**: Natural language questions about water resources (Russian/English)
- **Vector search**: Semantic search through passport documents and object metadata
- **Priority explanations**: AI-generated explanations for priority scores
- **Multi-tool orchestration**: Combines local knowledge base and web search

### Mobile Application

- **React Native Expo**: Cross-platform mobile app (iOS/Android)
- **Type-safe API integration**: Full backend connectivity with TypeScript types
- **Offline-first auth**: Secure JWT token storage with SecureStore
- **Face verification**: Biometric authentication support

## 🚀 Quick Start

### Full Stack Setup

#### Prerequisites

- **Backend**: Docker & Docker Compose, Python 3.12+, PostgreSQL 15+
- **Frontend**: Node.js 18+, npm/yarn, Expo CLI
- **API Keys**: Google API key (Gemini AI), Tavily API key (web search)

#### Installation

1. **Clone the repository**

```bash
git clone https://github.com/elitekbtu/promtech.git
cd promtech
```

2. **Configure backend environment**

```bash
cp env.example .env
```

Edit `.env` and set:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/gidroatlas
SECRET_KEY=your-secret-key-here
GOOGLE_API_KEY=your-google-api-key
TAVILY_API_KEY=your-tavily-api-key
```

3. **Configure frontend environment**

```bash
cd frontend
cp .env.example .env  # Create if doesn't exist
```

Edit `frontend/.env`:

```env
EXPO_PUBLIC_BACKEND_URL=http://localhost:8000
EXPO_PUBLIC_GEMINI_API_KEY=your-google-api-key
```

4. **Start backend services**

```bash
cd .. # Back to project root
docker compose up -d
```

4. **Access the application**

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### Initial Setup

1. **Seed reference data**

```bash
docker exec promtech-backend-1 python scripts/seed_reference_objects.py
docker exec promtech-backend-1 python scripts/seed_passport_texts.py
```

2. **Import water objects from OpenStreetMap** (optional)

```bash
docker exec promtech-backend-1 python scripts/import_osm_water.py
```

3. **Import passport PDFs** (if available)

```bash
docker exec promtech-backend-1 python scripts/seed_all_passports.py
```

4. **Enrich with real data**

```bash
docker exec promtech-backend-1 python scripts/enrich_water_objects.py
```

5. **Build RAG vector store**

```bash
docker exec promtech-backend-1 python rag_agent/scripts/rebuild_vector_store.py
```

## 📚 Documentation

- [Backend API Documentation](docs/backend.md) - Complete API reference
- [Backend Status](docs/BACKEND_STATUS.md) - Current implementation status
- [Testing Guide](backend/scripts/TESTING.md) - Test execution and validation
- [Data Import Guide](backend/scripts/DATA_IMPORT_GUIDE.md) - Data seeding procedures
- [Role System](docs/ROLES.md) - Authentication and authorization
- [Migration Guide](docs/MIGRATION.md) - Deployment and migration procedures

## 🏗️ Architecture

### Backend (FastAPI + Python)

```
backend/
├── main.py                 # Application entry point
├── database.py             # Database configuration
├── models/                 # SQLAlchemy models
│   ├── user.py            # User model (guest/expert roles)
│   ├── water_object.py    # WaterObject model with priority logic
│   └── passport_text.py   # PassportText model
├── services/              # Business logic modules
│   ├── auth/              # Authentication (login, register)
│   ├── objects/           # Water objects CRUD
│   ├── priorities/        # Priority dashboard
│   └── passports/         # Passport upload/extraction
├── rag_agent/             # RAG system
│   ├── config/            # LangGraph configuration
│   ├── tools/             # RAG tools (vector search, web search)
│   ├── routes/            # RAG endpoints
│   └── scripts/           # Vector store management
└── scripts/               # Data import and testing
```

### Frontend (React Native + Expo)

```
frontend/
├── app/                   # Application screens
├── components/            # Reusable components
├── hooks/                 # Custom hooks (auth, RAG)
├── lib/                   # API clients and utilities
└── contexts/              # React contexts
```

### Database Schema

**Users**

- `id`, `name`, `surname`, `email`, `phone`, `password_hash`
- `role`: `guest` | `expert`

**Water Objects**

- Core: `name`, `region`, `resource_type`, `water_type`, `fauna`
- Technical: `technical_condition`, `passport_date`, `pdf_url`
- Geographic: `latitude`, `longitude`
- Computed: `priority`, `priority_level`

**Passport Texts**

- `object_id` (FK to water_objects)
- `document_title`, `full_text`
- Sections: `general_info`, `technical_params`, `ecological_state`, `recommendations`

## 🔑 API Endpoints

### Authentication

```
POST   /api/auth/register      Register new user
POST   /api/auth/login         Login (returns JWT token)
GET    /api/auth/users/me      Get current user info
```

### Water Objects

```
GET    /api/objects            List objects (filtering, sorting, pagination)
GET    /api/objects/{id}       Get object by ID
GET    /api/objects/{id}/passport  Get passport metadata
```

### Priorities (Experts Only)

```
GET    /api/priorities/table   Priority dashboard table
GET    /api/priorities/stats   Priority statistics
```

### Passports

```
POST   /api/passports/upload   Upload passport PDF
GET    /api/passports/{object_id}  Retrieve passport text
```

### RAG System

```
POST   /api/rag/query          Submit natural language query
POST   /api/rag/explain-priority/{id}  Get priority explanation
```

### Face Verification

```
POST   /api/faceid/verify      Verify face match
```

## 🧪 Testing

Run the complete test suite:

```bash
python backend/scripts/run_all_tests.py
```

Individual tests:

```bash
# Priority calculation edge cases
docker exec promtech-backend-1 python scripts/test_priority_calculation.py

# Role-based access control
python backend/scripts/test_rbac.py

# Filtering, sorting, pagination
python backend/scripts/test_filtering_sorting.py

# RAG integration
python backend/scripts/test_rag_integration.py
```

See [TESTING.md](backend/scripts/TESTING.md) for detailed test documentation.

## 📊 Current Data

- **25 water objects** across Kazakhstan
- **22 passport documents** (88% coverage)
- **17 HIGH priority** objects (aging infrastructure from 1958-1987)
- **6 MEDIUM priority** objects
- **2 LOW priority** objects

Priority range: 3 to 76

## 🌐 Supported Languages

- **Russian**: Primary language for UI and queries
- **English**: API documentation and code
- **Kazakh**: Planned for future releases

## 🔧 Technology Stack

**Backend:**

- FastAPI 0.124.0
- SQLAlchemy 2.0
- PostgreSQL 15
- LangChain / LangGraph
- Google Gemini API
- Tavily Search API
- pypdf (PDF processing)
- FAISS (vector search)

**Frontend:**

- React Native
- Expo
- TypeScript
- Axios

**Infrastructure:**

- Docker & Docker Compose
- Uvicorn (ASGI server)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Elite Team - Terricon Valley, GidroAtlas**

- Backend Development
- Frontend Development
- AI/ML Integration
- Database Design

## 📧 Contact

Project Link: [https://github.com/elitekbtu/promtech](https://github.com/elitekbtu/promtech)

## 🙏 Acknowledgments

- Terricon Valley, GidroAtlas Organizers
- Ministry of Water Resources and Irrigation of Kazakhstan
- OpenStreetMap contributors
- Google Gemini AI team
- FastAPI community
