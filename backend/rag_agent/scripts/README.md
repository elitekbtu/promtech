# RAG System Scripts

This directory contains utility scripts for managing the RAG (Retrieval-Augmented Generation) system.

## Water Management Vector Store Initialization

### `initialize_water_vector_store.py`

This script indexes water management data into the vector store for semantic search.

**What it does:**

- Indexes all water objects from the database with formatted searchable text
- Indexes passport document sections with metadata
- Includes priority calculations and explanations in the indexed content
- Enriches documents with metadata for filtering (region, resource_type, priority_level, etc.)

**Usage:**

```bash
# From the backend directory
cd backend
python rag_agent/scripts/initialize_water_vector_store.py
```

**Requirements:**

- Database must be running and populated with water objects
- `GOOGLE_API_KEY` must be set in environment variables
- At least one water object should exist in the database

**What gets indexed:**

1. **Water Objects** - Each water object becomes a searchable document containing:

   - Name, region, coordinates
   - Resource type (lake/canal/reservoir) in Russian and English
   - Water type (fresh/non-fresh)
   - Fauna presence
   - Technical condition (1-5 scale with Russian descriptions)
   - Passport date and age
   - Priority score and level with calculation explanation
   - Warnings for outdated passports or high priority objects

2. **Passport Sections** - Each passport section becomes a separate document:
   - Full text
   - General information (Общая информация)
   - Technical parameters (Технические параметры)
   - Ecological state (Экологическое состояние)
   - Recommendations (Рекомендации)

**Metadata Structure:**

Each indexed document includes rich metadata for filtering:

- `object_id` - Water object ID
- `object_name` - Water object name
- `region` - Geographic region
- `resource_type` - Type of water body (lake/canal/reservoir)
- `water_type` - Water classification (fresh/non_fresh)
- `priority_level` - Priority classification (high/medium/low)
- `technical_condition` - Condition score (1-5)
- `section_type` - For passport sections (full_text/general_info/etc.)
- `document_type` - Either "water_object" or "passport_text"

**Example Queries After Indexing:**

```python
# Semantic search examples that will work:
"озера с высоким приоритетом в Алматинской области"
"water bodies with critical technical condition"
"водоемы с фауной возраст паспорта больше 5 лет"
"каналы непресная вода"
"passport information about Lake Balkhash"
"техническое состояние водохранилищ"
"priority calculation explanation"
```

**Re-indexing:**

Run this script again whenever:

- New water objects are added to the database
- Passport documents are uploaded or updated
- Water object data is modified (technical condition, priority, etc.)

The script will:

- Load existing vector store if present
- Add new water management documents
- Save the updated vector store

**Troubleshooting:**

If indexing fails:

1. Check database connection
2. Verify GOOGLE_API_KEY is set correctly
3. Ensure at least one water object exists: `SELECT COUNT(*) FROM water_objects;`
4. Check logs for detailed error messages

**Performance:**

- Indexing 100 water objects: ~30-60 seconds
- Indexing 1000 water objects: ~5-10 minutes
- Time depends on number of passport sections and network speed to Google API
