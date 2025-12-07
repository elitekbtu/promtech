# Change: Add Water Management System for GidroAtlas

## Why

The current backend is a generic user authentication and RAG system (labeled "Zamanbank API"). We need to transform it into **GidroAtlas** - a specialized water resource management system for Kazakhstan that:

- Maps and monitors water bodies (lakes, canals, reservoirs) and hydraulic structures
- Calculates inspection priorities based on technical condition and passport age
- Provides expert vs guest role-based access to priority information
- Enables AI-powered analysis of water resource passports and characteristics

This change implements the complete water management domain specified in the technical requirements.

## What Changes

### Core Domain Models

- **ADDED**: `WaterObject` model with geographic coordinates, resource type, water characteristics, technical condition (1-5 scale), and priority calculation
- **ADDED**: `PassportText` model for storing and searching water body passport documents
- **ADDED**: Priority calculation engine using formula: `(6 - technical_condition) * 3 + passport_age_years`
- **MODIFIED**: User model to support `guest` and `expert` roles (currently `admin`/`user`)

### API Endpoints

- **ADDED**: `/objects` - List/filter/sort water objects with pagination
- **ADDED**: `/objects/{id}` - Get detailed water object information
- **ADDED**: `/objects/{id}/passport` - Access passport metadata and documents
- **ADDED**: `/priorities/table` - Expert-only prioritization dashboard
- **MODIFIED**: `/api/auth/login` - Return role-based tokens with `guest`/`expert` roles
- **MODIFIED**: `/api/rag/query` - Adapt existing RAG endpoint to water management domain (search water objects, passport analysis, priority explanations)
- **ADDED**: `/api/rag/explain-priority/{object_id}` - Specialized endpoint for AI priority explanation (convenience wrapper over RAG query)

### Role-Based Access Control

- **MODIFIED**: Role system from `admin`/`user` to `guest`/`expert`
- **ADDED**: Guest role - view only, no access to priorities or detailed analytics
- **ADDED**: Expert role - full access including priorities, passport documents, AI analysis
- **ADDED**: Endpoint protection with `require_expert()` dependency

### RAG System Customization

- **ADDED**: Water object search tool for RAG agents
- **ADDED**: Passport content retrieval tool for RAG agents
- **ADDED**: Priority calculation explanation tool
- **MODIFIED**: System prompts to hydro-engineering and water management domain
- **MODIFIED**: Vector store to index passport documents instead of generic content

### Data Seeding

- **ADDED**: OSM/Overpass import script for Kazakhstan water bodies
- **ADDED**: Manual import process for reference objects (Barakkol, Koskol, Kamystykol lakes)
- **ADDED**: Passport document processing and text extraction

### Infrastructure

- **MODIFIED**: Project branding from "Zamanbank API" to "GidroAtlas"
- **ADDED**: File storage for passport PDFs with configurable `FILE_STORAGE_BASE_URL`
- **ADDED**: Environment variables for water management configuration

## Impact

### Affected Specifications

- `authentication` (new spec) - Guest/Expert role system
- `water-objects` (new spec) - Core water resource management
- `priority-system` (new spec) - Inspection priority calculation
- `passport-management` (new spec) - Document storage and retrieval
- `rag-system` (modified) - Domain-specific RAG for water management
- `api-endpoints` (new spec) - REST API design for water resources

### Affected Code

- `backend/models/` - Add WaterObject, PassportText models
- `backend/models/user.py` - Modify role enum
- `backend/main.py` - Update app title and route registration
- `backend/services/auth/` - Update role validation logic
- `backend/rag_agent/tools/` - Add water-specific tools (water_search, passport_retrieval, priority_explainer)
- `backend/rag_agent/config/orchestrator.py` - Configure water domain prompts
- `backend/rag_agent/routes/router.py` - Add priority explanation endpoint
- `backend/rag_agent/utils/vector_store.py` - Modify to index passport documents
- New modules:
  - `backend/services/objects/` - Water object CRUD and filtering
  - `backend/services/priorities/` - Priority calculation and dashboard
  - `backend/services/passports/` - Document management
- New scripts:
  - `backend/scripts/import_osm_water.py` - Data seeding

### Breaking Changes

- **BREAKING**: User role field changes from `admin`/`user` to `guest`/`expert`
- **BREAKING**: Authentication response changes to include role-based JWT
- **BREAKING**: RAG query context changes to water management domain
- **BREAKING**: Application rebranded from "Zamanbank API" to "GidroAtlas"

### Migration Required

- Existing users need role migration: `admin` → `expert`, `user` → `guest`
- RAG vector store needs to be rebuilt with passport documents
- Frontend needs updates to consume new water object APIs

### Dependencies

- No new external dependencies required
- Existing stack (FastAPI, PostgreSQL, DeepFace, LangChain, Gemini) sufficient
- Optional: pypdf for passport text extraction (already in requirements.txt)

### Deployment Considerations

- Database migration needed for new models
- Environment variables: `FILE_STORAGE_BASE_URL`, `FILE_STORAGE_PATH`
- Initial data import from OSM required
- Passport documents need to be uploaded/ingested
