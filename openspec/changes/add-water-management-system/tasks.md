# Implementation Tasks

## 1. Database Models & Schema

- [ ] 1.1 Create `WaterObject` SQLAlchemy model with all fields (name, region, resource_type, water_type, fauna, passport_date, technical_condition, lat/lon, pdf_url, priority, priority_level)
- [ ] 1.2 Create `PassportText` model for storing passport document text with sections
- [ ] 1.3 Modify `User` model role field from `admin`/`user` enum to `guest`/`expert`
- [ ] 1.4 Create database migration script (Alembic) for new models
- [ ] 1.5 Add indexes on frequently queried fields (region, resource_type, priority, technical_condition)

## 2. Core Business Logic

- [ ] 2.1 Implement priority calculation function: `(6 - technical_condition) * 3 + passport_age_years`
- [ ] 2.2 Implement priority level mapping (high/medium/low based on score)
- [ ] 2.3 Create water object service layer with CRUD operations
- [ ] 2.4 Implement filtering logic (region, resource_type, water_type, fauna, date ranges, technical_condition)
- [ ] 2.5 Implement sorting logic (all WaterObject fields)
- [ ] 2.6 Implement pagination helpers

## 3. API Endpoints - Water Objects

- [ ] 3.1 Create `backend/services/objects/router.py` with endpoint structure
- [ ] 3.2 Implement `GET /objects` with query params for filtering/sorting/pagination
- [ ] 3.3 Implement role-based response (exclude priority fields for guests)
- [ ] 3.4 Implement `GET /objects/{id}` with role-based field filtering
- [ ] 3.5 Implement `GET /objects/{id}/passport` for passport metadata
- [ ] 3.6 Create Pydantic schemas for requests/responses in `schemas.py`
- [ ] 3.7 Add service layer business logic in `service.py`

## 4. API Endpoints - Priorities

- [ ] 4.1 Create `backend/services/priorities/router.py`
- [ ] 4.2 Implement `GET /priorities/table` with expert-only protection
- [ ] 4.3 Implement filtering/sorting specific to priority dashboard
- [ ] 4.4 Create `require_expert()` dependency for endpoint protection
- [ ] 4.5 Create Pydantic schemas for priority responses

## 5. Authentication Updates

- [ ] 5.1 Update `backend/services/auth/schemas.py` role enum to `guest`/`expert`
- [ ] 5.2 Modify login endpoint to return JWT with new role field
- [ ] 5.3 Update `UserRead` schema to reflect new role values
- [ ] 5.4 Create role validation dependencies (`get_current_user_role`, `require_expert`)
- [ ] 5.5 Update user registration to default to `guest` role

## 6. Passport Management

- [ ] 6.1 Create `backend/services/passports/` module structure
- [ ] 6.2 Implement file upload handler for PDF passports
- [ ] 6.3 Implement PDF text extraction using pypdf
- [ ] 6.4 Create passport text storage service (save to `PassportText` model)
- [ ] 6.5 Implement passport retrieval by object_id
- [ ] 6.6 Configure file storage path and base URL from environment variables

## 7. RAG System Customization

- [ ] 7.1 Create `backend/rag_agent/tools/water_search.py` - search_water_objects tool
- [ ] 7.2 Create `backend/rag_agent/tools/passport_retrieval.py` - get_passport_content tool
- [ ] 7.3 Create `backend/rag_agent/tools/priority_explainer.py` - explain_priority_logic tool
- [ ] 7.4 Update orchestrator system prompts to hydro-engineering domain
- [ ] 7.5 Modify vector store initialization to index passport documents
- [ ] 7.6 Remove or adapt generic web search tool (Tavily) for water management context

## 8. AI Endpoints

- [ ] 8.1 Create `backend/services/ai/router.py` for domain-specific AI endpoints
- [ ] 8.2 Implement `POST /ai/chat` - general water management chat
- [ ] 8.3 Implement `POST /ai/objects/{id}/explain-priority` - priority explanation
- [ ] 8.4 Implement `POST /ai/search` - natural language search
- [ ] 8.5 Create `GeminiAgentService` facade over LangGraph
- [ ] 8.6 Integrate water object and passport tools into agent workflow
- [ ] 8.7 Create response schemas for AI endpoints

## 9. Data Seeding & Import

- [ ] 9.1 Create `backend/scripts/import_osm_water.py` script
- [ ] 9.2 Implement Overpass API query for Kazakhstan water bodies
- [ ] 9.3 Parse OSM data into WaterObject format
- [ ] 9.4 Implement bulk insert of water objects
- [ ] 9.5 Create manual import process for reference objects (Barakkol, Koskol, Kamystykol)
- [ ] 9.6 Add sample passport documents to seed data
- [ ] 9.7 Create documentation for data import process

## 10. Configuration & Environment

- [ ] 10.1 Add `FILE_STORAGE_PATH` to .env.example
- [ ] 10.2 Add `FILE_STORAGE_BASE_URL` to .env.example
- [ ] 10.3 Update `backend/database.py` if needed for new models
- [ ] 10.4 Update `backend/main.py` app title to "GidroAtlas API"
- [ ] 10.5 Register all new routers in main.py
- [ ] 10.6 Update CORS settings if needed

## 11. Testing & Validation

- [ ] 11.1 Create test data (10+ water objects with varying priorities)
- [ ] 11.2 Test priority calculation with edge cases
- [ ] 11.3 Test role-based access control (guest cannot access priorities)
- [ ] 11.4 Test filtering/sorting/pagination combinations
- [ ] 11.5 Test passport upload and text extraction
- [ ] 11.6 Test AI endpoints with sample queries
- [ ] 11.7 Test RAG tools integration
- [ ] 11.8 Verify OpenAPI documentation at /docs

## 12. Documentation Updates

- [ ] 12.1 Update README.md with GidroAtlas description
- [ ] 12.2 Document new API endpoints in backend.md
- [ ] 12.3 Document role system changes
- [ ] 12.4 Create migration guide for existing deployments
- [ ] 12.5 Document data import procedures
- [ ] 12.6 Update environment variable documentation

## 13. Migration & Deployment

- [ ] 13.1 Create database migration script (Alembic)
- [ ] 13.2 Create user role migration script (admin→expert, user→guest)
- [ ] 13.3 Test migration on staging environment
- [ ] 13.4 Backup existing data before production migration
- [ ] 13.5 Run migrations in production
- [ ] 13.6 Verify all endpoints functioning post-migration
- [ ] 13.7 Rebuild RAG vector store with passport documents
