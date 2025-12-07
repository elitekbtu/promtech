# Design: Water Management System Architecture

## Context

Transforming a generic authentication + RAG backend into a specialized water resource management system (GidroAtlas) for Kazakhstan. The system needs to:

- Store and manage water bodies with geographic and technical data
- Calculate inspection priorities based on condition and document age
- Provide differentiated access for guests (public view) vs experts (full analytics)
- Enable AI-powered analysis of water resource characteristics through passport documents

**Stakeholders**: Water resource engineers, government agencies, public users  
**Constraints**:

- Must maintain existing RAG and face ID capabilities
- PostgreSQL-only (no additional databases)
- Docker deployment required
- Must work with existing Gemini API integration

## Goals / Non-Goals

**Goals:**

- Complete domain transformation to water management
- Maintain clean modular architecture
- Support 100s-1000s of water objects with efficient querying
- Enable role-based data visibility (guest vs expert)
- Integrate water domain knowledge into RAG system

**Non-Goals:**

- Real-time sensor data integration (future phase)
- Mobile offline support
- Multi-language interface (Russian only for MVP)
- Advanced GIS features (basic lat/lon sufficient)
- Historical trend analysis (future phase)

## Decisions

### Decision 1: Modular Monolith Architecture

**What**: Organize by feature domains (objects, priorities, passports, ai) rather than technical layers  
**Why**:

- Clear boundaries between water management concerns
- Easy to locate and modify related code
- Can extract to microservices later if needed
- Matches existing auth/faceid structure

**Structure**:

```
backend/
├── models/
│   ├── user.py (modified)
│   ├── water_object.py (new)
│   └── passport_text.py (new)
├── services/
│   ├── auth/ (modified)
│   ├── objects/ (new) - Water object CRUD
│   ├── priorities/ (new) - Priority dashboard
│   └── passports/ (new) - Document management
└── rag_agent/ (modified) - Water domain tools + enhanced query endpoint
```

**Alternatives Considered**:

- Single `water_management/` module: Too monolithic, harder to navigate
- Technical layers (controllers/services/repos): More boilerplate, less domain clarity
- New `backend/services/ai/` module: REJECTED - creates duplication with existing rag_agent/

### Decision 2: Priority as Computed Field

**What**: Store priority as calculated integer in database, compute on write  
**Why**:

- Fast sorting and filtering (indexed column)
- No computation overhead on reads (most common operation)
- Simple SQL queries for priority ranges
- Can rebuild easily if formula changes

**Formula**: `priority = (6 - technical_condition) * 3 + (current_year - passport_year)`

**Alternatives Considered**:

- Compute on read: Too slow for sorting/filtering across large datasets
- Materialized view: Overkill for simple calculation, harder to maintain
- Separate priority table: Unnecessary join overhead

### Decision 3: Guest vs Expert Role Strategy

**What**: Return different response schemas based on role, enforce at serialization layer  
**Why**:

- Security: Guests never see priority data in responses
- Performance: Single query, filter fields afterward
- Flexibility: Easy to add more role-based fields
- Clean: Pydantic schemas handle conditional inclusion

**Implementation**:

```python
def get_objects(role: str, ...):
    objects = query_database(...)
    if role == "guest":
        return [ObjectPublicSchema.model_validate(obj) for obj in objects]
    else:
        return [ObjectExpertSchema.model_validate(obj) for obj in objects]
```

**Alternatives Considered**:

- Separate endpoints (/public/objects, /expert/objects): API duplication
- Database-level filtering: More complex queries, harder to maintain
- Claims-based JWT: Overkill for two simple roles

### Decision 4: Passport Storage Strategy

**What**: Store PDF files locally, extract text to PostgreSQL table for RAG  
**Why**:

- Simple deployment (no S3 dependency for MVP)
- Full-text search in PostgreSQL
- RAG can query text without file I/O
- Files accessible via URL for download

**Storage**:

- PDFs: `{FILE_STORAGE_PATH}/passports/{object_id}.pdf`
- Text: `passport_texts` table with sections (physical, biological, productivity)
- URL: `{FILE_STORAGE_BASE_URL}/passports/{object_id}.pdf`

**Alternatives Considered**:

- S3/MinIO: Extra infrastructure, can add later
- Store text in vector DB only: Loses structured section information
- Parse on-demand: Too slow, unnecessary I/O

### Decision 5: RAG Tool Architecture

**What**: Create three specialized tools for water domain  
**Why**:

- LangGraph agents can choose appropriate tool
- Clear separation of concerns
- Easy to test independently
- Extensible for future tools

**Tools**:

1. `search_water_objects(filters)` - SQL query wrapper
2. `get_passport_content(object_id, sections)` - Text retrieval
3. `explain_priority_logic(object_id)` - Priority breakdown

**Alternatives Considered**:

- Single universal tool: Less precise, harder for agent to choose
- Direct database access: No validation, security risk
- Separate RAG chains: More complex orchestration

### Decision 6: Data Seeding from OSM

**What**: One-time import from OpenStreetMap Overpass API  
**Why**:

- Bootstraps system with real Kazakhstan water bodies
- Gets accurate coordinates and basic metadata
- Public domain data, no licensing issues

**Process**:

1. Query Overpass for water bodies in Kazakhstan
2. Map to WaterObject schema (name, lat/lon, type)
3. Bulk insert with default values (condition=3, no passport)
4. Manual enrichment for priority objects

**Alternatives Considered**:

- Government database APIs: May not exist or require credentials
- Manual entry: Too slow, error-prone
- Continuous sync: Overkill, water bodies rarely change

## Technical Specifications

### Database Schema

**water_objects**:

```sql
CREATE TABLE water_objects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    resource_type VARCHAR(20) NOT NULL, -- lake, canal, reservoir
    water_type VARCHAR(20) NOT NULL,    -- fresh, non_fresh
    fauna BOOLEAN NOT NULL DEFAULT false,
    passport_date DATE,
    technical_condition INTEGER CHECK (technical_condition BETWEEN 1 AND 5),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    pdf_url VARCHAR(500),
    priority INTEGER,
    priority_level VARCHAR(10),         -- high, medium, low
    osm_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_water_objects_region ON water_objects(region);
CREATE INDEX idx_water_objects_priority ON water_objects(priority DESC);
CREATE INDEX idx_water_objects_resource_type ON water_objects(resource_type);
CREATE INDEX idx_water_objects_location ON water_objects(latitude, longitude);
```

**passport_texts**:

```sql
CREATE TABLE passport_texts (
    id SERIAL PRIMARY KEY,
    object_id INTEGER REFERENCES water_objects(id) ON DELETE CASCADE,
    section VARCHAR(50) NOT NULL,  -- physical, biological, productivity
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_passport_texts_object ON passport_texts(object_id);
CREATE INDEX idx_passport_texts_section ON passport_texts(section);
```

**users** (modified):

```sql
ALTER TABLE users
ALTER COLUMN role TYPE VARCHAR(20);

-- Migration script will update:
-- 'admin' -> 'expert'
-- 'user' -> 'guest'
```

### API Response Examples

**GET /objects?region=Улытауская&priority_level=high (expert)**:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Бараккол",
      "region": "Улытауская область",
      "resource_type": "lake",
      "water_type": "non_fresh",
      "fauna": true,
      "passport_date": "2016-01-01",
      "technical_condition": 4,
      "latitude": 49.3147,
      "longitude": 67.2756,
      "pdf_url": "http://localhost:8000/storage/passports/1.pdf",
      "priority": 14,
      "priority_level": "high"
    }
  ],
  "total": 3,
  "page": 1,
  "page_size": 20
}
```

**Same query (guest)**:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Бараккол",
      "region": "Улытауская область",
      "resource_type": "lake",
      "water_type": "non_fresh",
      "fauna": true,
      "passport_date": "2016-01-01",
      "latitude": 49.3147,
      "longitude": 67.2756
      // No technical_condition, priority, priority_level
    }
  ],
  "total": 3,
  "page": 1,
  "page_size": 20
}
```

### RAG System Integration

**System Prompt** (water domain):

```
Ты — помощник по гидротехническим сооружениям и водным ресурсам Казахстана.
У тебя есть доступ к базе данных водных объектов и их паспортов.

Доступные инструменты:
- search_water_objects: Поиск водоёмов по фильтрам
- get_passport_content: Чтение паспортов объектов
- explain_priority_logic: Объяснение приоритета обследования

Отвечай точно, основываясь только на доступных данных.
```

**Tool Schemas**:

```python
class SearchWaterObjectsTool:
    name = "search_water_objects"
    description = "Search for water bodies by region, type, condition, priority"

    def run(self, region: str = None, resource_type: str = None,
            priority_level: str = None, limit: int = 10) -> List[Dict]:
        # Query database with filters
        # Return object summaries

class GetPassportContentTool:
    name = "get_passport_content"
    description = "Retrieve passport document sections for a water object"

    def run(self, object_id: int, sections: List[str] = None) -> Dict:
        # Fetch from passport_texts table
        # Return structured text by section

class ExplainPriorityTool:
    name = "explain_priority_logic"
    description = "Explain why object has specific inspection priority"

    def run(self, object_id: int) -> Dict:
        # Get object details
        # Calculate priority components
        # Return human-readable explanation
```

## Risks / Trade-offs

### Risk: Data Quality

**Risk**: OSM data may be incomplete or inaccurate for technical details  
**Mitigation**:

- Use OSM for coordinates and names only
- Manual verification for priority objects
- Clear UI indicators for data completeness
- Admin interface for corrections (future)

### Risk: Priority Formula Accuracy

**Risk**: Simple formula may not capture real inspection urgency  
**Mitigation**:

- Formula is configurable via code (easy to adjust)
- Priority stored in DB, can recalculate all objects
- Expert feedback loop for tuning
- Document formula limitations

### Risk: Performance at Scale

**Risk**: Filtering/sorting 10,000+ objects may be slow  
**Mitigation**:

- Database indexes on all filter fields
- Pagination mandatory (max 100/page)
- Consider query caching for common filters
- Monitor query performance metrics

### Trade-off: Local File Storage

**Pro**: Simple deployment, no cloud dependencies  
**Con**: Not suitable for multi-server deployment, no CDN  
**Decision**: Accept for MVP, plan S3 migration for production scale

### Trade-off: Role Simplicity

**Pro**: Easy to understand and implement (2 roles)  
**Con**: May need more granular permissions later  
**Decision**: Accept for MVP, roles are extensible if needed

## Migration Plan

### Phase 1: Database Migration (Zero Downtime)

1. Add new tables (`water_objects`, `passport_texts`) via Alembic
2. Modify `users.role` column (add new enum values first, then migrate data)
3. Run data migration script: `UPDATE users SET role = 'expert' WHERE role = 'admin'`
4. Test rollback procedure

### Phase 2: Code Deployment

1. Deploy new backend code (new routes won't be called yet)
2. Verify existing auth/faceid/rag endpoints still work
3. Test new water management endpoints in staging
4. Smoke test all modules

### Phase 3: Data Import

1. Run OSM import script for Kazakhstan
2. Validate imported objects
3. Import reference objects with passports
4. Rebuild RAG vector store

### Phase 4: Frontend Cutover

1. Deploy frontend updates to use new API
2. Monitor error rates
3. Verify role-based access working
4. Rollback plan: point frontend back to old endpoints (not applicable - new domain)

### Rollback Strategy

**Database**: Keep old tables until migration verified (1 week)  
**Code**: Git revert + redeploy previous version  
**Data**: Database backup before migration  
**Note**: Full rollback not possible after water objects imported (new domain)

## Open Questions

1. **Passport Document Format**: Are actual PDF passports available, or just text data?

   - **Resolution**: Assume PDFs available, text extraction with pypdf

2. **Real-time Updates**: How often do water objects data change?

   - **Assumption**: Static/slow-changing (monthly), no real-time sync needed

3. **Coordinate System**: What projection/datum for lat/lon?

   - **Assumption**: WGS84 (standard for web maps)

4. **Priority Access**: Can guests see that priority exists but not the value?

   - **Decision**: No - completely hide priority concept from guests

5. **Multilingual Support**: Russian only or need Kazakh?

   - **Assumption**: Russian only for MVP, i18n later

6. **Authentication**: Keep face ID for water management domain?
   - **Decision**: Yes, keep existing auth mechanisms, just add new roles
