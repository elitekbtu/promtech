# OpenSpec Change Proposal: Water Management System

## Status: 🚧 In Progress - Phase 3/13

**Phase 1 ✅ COMPLETED** - Database Models & Schema (5/5 tasks)  
**Phase 2 ✅ COMPLETED** - Core Business Logic (6/6 tasks)  
**Phase 3 🔄 NEXT** - API Endpoints - Water Objects (7 tasks)

I've created a comprehensive OpenSpec change proposal to transform your current backend (Zamanbank API) into **GidroAtlas** - a water resource management system for Kazakhstan.

## 📁 Location

`openspec/changes/add-water-management-system/`

## 📋 What's Included

### 1. **proposal.md** - Executive Summary

- Why: Transform generic backend into specialized water management system
- What: Complete domain transformation with new models, APIs, roles, and AI capabilities
- Impact: Breaking changes to roles, new water object domain, RAG customization

### 2. **tasks.md** - Implementation Checklist (82 tasks)

Organized into 13 phases:

1. Database Models & Schema (5 tasks)
2. Core Business Logic (6 tasks)
3. API Endpoints - Water Objects (7 tasks)
4. API Endpoints - Priorities (5 tasks)
5. Authentication Updates (5 tasks)
6. Passport Management (6 tasks)
7. RAG System Customization (7 tasks)
8. RAG Endpoint Enhancements (7 tasks)
9. Data Seeding & Import (7 tasks)
10. Configuration & Environment (6 tasks)
11. Testing & Validation (8 tasks)
12. Documentation Updates (6 tasks)
13. Migration & Deployment (7 tasks)

### 3. **design.md** - Technical Architecture

Comprehensive design document covering:

- **Context & Goals**: Water management system requirements
- **6 Key Decisions**:
  - Modular monolith architecture
  - Priority as computed field
  - Guest vs Expert role strategy
  - Passport storage (local files + PostgreSQL text)
  - RAG tool architecture (3 specialized tools)
  - OSM data seeding
- **Database Schema**: Complete DDL with indexes
- **API Examples**: Request/response formats
- **RAG Integration**: System prompts and tool schemas
- **Risks & Trade-offs**: Data quality, performance, storage
- **Migration Plan**: 4-phase deployment strategy
- **Open Questions**: Documented assumptions

### 4. **specs/** - Requirements (6 capabilities)

#### `water-objects/spec.md`

- Water object data model (12 fields)
- Filtering by 7+ dimensions
- Sorting and pagination
- Role-based field visibility
- Bulk operations

#### `priority-system/spec.md`

- Priority calculation formula
- 3-level classification (high/medium/low)
- Automatic updates
- Expert-only dashboard
- Bulk recalculation

#### `authentication/spec.md`

- **MODIFIED**: Role system (admin/user → guest/expert)
- **ADDED**: JWT role claims
- **ADDED**: Role migration procedures
- **ADDED**: Expert-only endpoint protection

#### `passport-management/spec.md`

- PDF document storage
- Text extraction (pypdf)
- Sectioned storage (physical/biological/productivity)
- Metadata access
- File validation
- Bulk processing

#### `rag-system/spec.md`

- **MODIFIED**: Domain-specific prompts (hydro-engineering)
- **ADDED**: 3 specialized tools:
  - `search_water_objects` - SQL filtering
  - `get_passport_content` - Document retrieval
  - `explain_priority_logic` - Priority analysis
- Vector store with passports
- Context management
- Source citation

#### `rag-enhancements/spec.md`

- MODIFIED `/api/rag/query` endpoint for water queries
- ADDED `/api/rag/explain-priority/{object_id}` convenience endpoint (expert-only)
- Enhanced QueryRequest/QueryResponse schemas
- Domain-specific response formatting
- Error handling
- Response caching

## 🎯 Implementation Progress

### ✅ Completed Phases

#### Phase 1: Database Models & Schema (5/5 tasks) ✅

- [x] WaterObject SQLAlchemy model with enums (ResourceType, WaterType, FaunaType, PriorityLevel)
- [x] PassportText model with structured sections
- [x] User model updated (guest/expert roles)
- [x] Alembic migration created and applied
- [x] Database indexes on key fields

**Deliverables:**

- `backend/models/water_object.py` (140 lines)
- `backend/models/passport_text.py` (35 lines)
- `backend/models/user.py` (modified with UserRole enum)
- `backend/alembic/versions/933ade9f4842_*.py` (migration)
- Database tables: `water_objects`, `passport_texts`, `users` with proper enums

#### Phase 2: Core Business Logic (6/6 tasks) ✅

- [x] Priority calculation: `(6 - technical_condition) * 3 + passport_age_years`
- [x] Priority level mapping (HIGH ≥10, MEDIUM 6-9, LOW ≤5)
- [x] WaterObjectService with CRUD operations
- [x] Filtering (11 parameters: region, resource_type, water_type, fauna, technical_condition, priority, dates)
- [x] Sorting (any field, asc/desc)
- [x] Pagination helpers (limit/offset with total count)

**Deliverables:**

- `backend/services/objects/schemas.py` (150+ lines, 8 Pydantic schemas)
- `backend/services/objects/service.py` (290+ lines, 10 methods)
- Tested: 9 priority calculation tests ✅
- Tested: 8 CRUD integration tests ✅

### 🔄 Next Phase

#### Phase 3: API Endpoints - Water Objects (0/7 tasks)

- [ ] 3.1 Create `backend/services/objects/router.py`
- [ ] 3.2 Implement `GET /objects` with filtering/sorting/pagination
- [ ] 3.3 Role-based response (exclude priority for guests)
- [ ] 3.4 Implement `GET /objects/{id}`
- [ ] 3.5 Implement `GET /objects/{id}/passport`
- [ ] 3.6 Create Pydantic schemas (already done in Phase 2)
- [ ] 3.7 Add service layer business logic (already done in Phase 2)

---

## ✅ Validation Results

```bash
✓ Change 'add-water-management-system' is valid
```

All requirements have:

- At least one scenario (required)
- Proper formatting (#### Scenario: format)
- Clear GIVEN-WHEN-THEN structure
- Appropriate operation markers (ADDED/MODIFIED)

## 📊 Metrics

- **Total Capabilities**: 6 (5 new + 1 modified)
- **Total Requirements**: 40+
- **Total Scenarios**: 100+
- **Implementation Tasks**: 86
- **Breaking Changes**: 4 major

## 🚀 Next Steps

### For Review:

1. Read `proposal.md` for high-level overview
2. Review `design.md` for architectural decisions
3. Check `tasks.md` for implementation scope
4. Review each spec delta for requirements clarity

### For Implementation (after approval):

1. Start with Phase 1: Database Models (tasks 1.1-1.5)
2. Follow tasks.md sequentially
3. Mark each task `[x]` when complete
4. Run tests after each major phase
5. Update documentation as you go

### For Archiving (after deployment):

```bash
openspec archive add-water-management-system --yes
```

## 🔑 Key Features

**New Domain Models:**

- `WaterObject` - Core water body data
- `PassportText` - Document text storage

**New API Endpoints:**

- `GET /objects` - List/filter water objects
- `GET /objects/{id}` - Object details
- `GET /objects/{id}/passport` - Passport metadata
- `GET /priorities/table` - Expert dashboard
- `POST /api/rag/query` - MODIFIED for water management queries
- `POST /api/rag/explain-priority/{object_id}` - Priority explanation (expert-only)

**Role System:**

- `guest` → View objects only (no priorities)
- `expert` → Full access + analytics

**RAG Customization:**

- Hydro-engineering domain prompts
- Water object search tool
- Passport content retrieval
- Priority explanation

## 📖 Documentation

All specs follow OpenSpec format with:

- Clear requirement statements (SHALL)
- Concrete scenarios with GIVEN-WHEN-THEN
- Proper operation markers (ADDED/MODIFIED)
- Domain-specific examples (Russian terminology)

## 💡 Design Highlights

1. **Clean Architecture**: Modular by domain (objects/priorities/passports/ai)
2. **Performance**: Indexed priority field, paginated queries
3. **Security**: Role-based access, JWT claims
4. **Scalability**: Local storage for MVP, S3-ready for production
5. **AI Integration**: Specialized RAG tools for water domain
6. **Data Quality**: OSM seeding + manual enrichment

## ⚠️ Breaking Changes

1. User roles: `admin`/`user` → `guest`/`expert`
2. Authentication response includes new role claim
3. RAG system repurposed for water domain
4. Application branding: "Zamanbank API" → "GidroAtlas"

## 📝 Migration Required

- Database: New tables + role field update
- Users: Role migration script (admin→expert, user→guest)
- RAG: Vector store rebuild with passport documents
- Frontend: API integration updates

---

**Status**: Ready for approval and implementation  
**Validation**: Passed strict checks  
**Estimated Effort**: Large (86 tasks across 13 phases)  
**Risk Level**: Medium (breaking changes, domain shift)
