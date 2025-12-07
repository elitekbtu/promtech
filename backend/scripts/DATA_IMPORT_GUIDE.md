# Data Import Guide

This guide explains how to import water object data into the GidroAtlas system.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Reference Objects (Quick Start)](#reference-objects-quick-start)
4. [OSM Import (Large Scale)](#osm-import-large-scale)
5. [Vector Store Indexing](#vector-store-indexing)
6. [Troubleshooting](#troubleshooting)

---

## Overview

GidroAtlas supports two methods for importing water object data:

1. **Reference Objects**: Manual seed data for testing and development
2. **OSM Import**: Automated import from OpenStreetMap for production data

After importing water objects, you need to rebuild the RAG vector store to enable semantic search.

---

## Prerequisites

### 1. Database Setup

Ensure database migrations are applied:

```bash
cd backend
alembic upgrade head
```

### 2. Python Dependencies

Install required packages (should already be in requirements.txt):

```bash
pip install requests sqlalchemy
```

### 3. Docker Environment (Recommended)

If using Docker, exec into the backend container:

```bash
docker exec -it promtech-backend-1 bash
cd /backend
```

---

## Reference Objects (Quick Start)

Reference objects are predefined test data from the hackathon documentation. Perfect for development and testing.

### Step 1: Seed Reference Water Objects

```bash
python scripts/seed_reference_objects.py
```

This will import 5 reference objects:

- **Коскол** (Lake, Ulytau region)
- **Камыстыкол** (Lake, Ulytau region)
- **Бухтарминский судоходный шлюз** (Lock, West Kazakhstan)
- **Шульбинский судоходный шлюз** (Lock, North Kazakhstan)
- **Чаглинский гидроузел** (Hydroelectric complex, East Kazakhstan)

**Output:**

```
======================================================================
Seeding Reference Water Objects
======================================================================
✓ Seeded Коскол (ID: 1, Priority: 9, Level: medium)
✓ Seeded Камыстыкол (ID: 2, Priority: 6, Level: medium)
...
======================================================================
Seeded 5 reference objects
======================================================================
```

### Step 2: Seed Passport Text Data

```bash
python scripts/seed_passport_texts.py
```

This will add detailed passport sections for reference objects:

- Geographic location
- Physical characteristics
- Biological characteristics
- Hydrological regime (for some objects)

**Output:**

```
======================================================================
Seeding Passport Text Data
======================================================================

📄 Seeding passport for Коскол...
  ✓ Seeded section 1: Географическое расположение
  ✓ Seeded section 2: Физическая характеристика
  ✓ Seeded section 3: Биологическая характеристика
  → Seeded 3 sections for Коскол

📄 Seeding passport for Камыстыкол...
  ✓ Seeded section 1: Географическое расположение
  ✓ Seeded section 2: Физическая характеристика
  ✓ Seeded section 3: Биологическая характеристика
  ✓ Seeded section 4: Гидрологический режим
  → Seeded 4 sections for Камыстыкол

======================================================================
Total passport sections seeded: 7
======================================================================
```

### Step 3: Rebuild Vector Store (Critical!)

After seeding data, rebuild the RAG vector store:

```bash
python rag_agent/scripts/rebuild_vector_store.py
```

This will index:

- Water object metadata (name, region, resource type, priority)
- Passport text sections (geographic, physical, biological data)

---

## OSM Import (Large Scale)

For production, import water bodies from OpenStreetMap covering all of Kazakhstan.

### How It Works

The OSM import script:

1. Queries Overpass API for water bodies in Kazakhstan bounding box
2. Filters for named lakes, rivers, canals, and reservoirs
3. Parses OSM tags into WaterObject format
4. Bulk inserts into database with default values

**Data Sources:**

- `natural=water` with `water=lake|reservoir|canal|river`
- `waterway=riverbank` (river areas)
- `waterway=river` (river ways with names)

### Usage

**Test Run (Limited):**

```bash
python scripts/import_osm_water.py --limit 50 --dry-run
```

This will:

- Fetch 50 objects from OSM
- Parse and validate data
- Show sample results
- **NOT** insert into database

**Production Import:**

```bash
python scripts/import_osm_water.py
```

This will:

- Fetch ALL water bodies in Kazakhstan (~1000-5000 objects)
- Parse and validate
- Bulk insert into database in batches of 100
- May take 5-15 minutes depending on Overpass API load

**Import with Limit (Testing):**

```bash
python scripts/import_osm_water.py --limit 500
```

### Expected Output

```
======================================================================
OSM Water Bodies Import for Kazakhstan
======================================================================

Bounding box: {'south': 40.5, 'north': 55.5, 'west': 46.5, 'east': 87.5}
Limit: None (import all)
Dry run: False

Querying Overpass API (attempt 1/3)...

Fetched 2847 elements from OSM

Parsing OSM elements...
Parsed 2341 valid water objects

Sample objects:
  - Балхаш (lake) at 46.8312, 74.9853
  - Каспийское море (lake) at 45.2156, 51.3421
  - Или (river) at 43.6521, 77.2341

Inserting 2341 objects into database...
Inserted batch 1: 100 objects (total: 100)
Inserted batch 2: 100 objects (total: 200)
...
Inserted batch 24: 41 objects (total: 2341)

✓ Successfully imported 2341 water objects

Import complete: 2341 objects
```

### Limitations & Notes

1. **Region Names**: Currently set to "Неизвестная область" (Unknown region)

   - Can be enhanced with reverse geocoding API (Nominatim)
   - Or manually updated via SQL after import

2. **Water Type**: Defaults to "fresh" (пресная)

   - Salt lakes detected by name keywords (соленое, солёное)
   - Can be refined with additional data sources

3. **Technical Condition**: Defaults to 3 (middle value)

   - Real values should come from inspection reports
   - Update manually or via separate data pipeline

4. **Passport Date**: Defaults to NULL

   - Real passport dates must be added separately

5. **Priority Calculation**: Automatic based on technical_condition and passport_age
   - Will be LOW until real passport data added

### API Rate Limits

Overpass API has rate limits:

- 2 concurrent connections per IP
- Fair use policy (don't hammer the server)
- If you get 429 errors, the script will retry with exponential backoff

---

## Vector Store Indexing

After importing ANY water object data, you **must** rebuild the vector store for RAG to work.

### Rebuild Script

```bash
python rag_agent/scripts/rebuild_vector_store.py
```

### What Gets Indexed

1. **Water Object Metadata:**

   ```
   Название: Коскол
   Регион: Улытауская область
   Тип ресурса: Озеро
   Приоритет: 9 (средний)
   Техническое состояние: 3
   ```

2. **Passport Text Sections:**
   ```
   Объект: Коскол
   Раздел 1: Географическое расположение
   Административная область: Улытауская область
   ...
   ```

### Verification

After rebuild, test the RAG system:

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "покажи озера с высоким приоритетом"}'
```

You should see water object metadata in the response sources.

---

## Troubleshooting

### Script Errors

**Error: `ModuleNotFoundError: No module named 'database'`**

Solution: Run scripts from backend directory:

```bash
cd backend
python scripts/seed_reference_objects.py
```

**Error: `Connection refused` (database)**

Solution: Ensure PostgreSQL is running:

```bash
docker-compose ps
# If stopped:
docker-compose up -d
```

**Error: `alembic.util.exc.CommandError: Can't locate revision identified by...`**

Solution: Reset migrations and run again:

```bash
alembic downgrade base
alembic upgrade head
```

### OSM Import Issues

**Error: `Request failed: 429 Too Many Requests`**

Solution: Overpass API rate limit hit. Wait 5 minutes and retry.

**Error: `Request failed: timeout`**

Solution: Query is too large. Use `--limit` to reduce:

```bash
python scripts/import_osm_water.py --limit 1000
```

**Warning: `Parsed 0 valid water objects`**

Solution: OSM data might be empty for region. Check query manually:

- Visit https://overpass-turbo.eu/
- Paste query from script output
- Verify data exists

### Vector Store Issues

**Error: `ValueError: No documents to index`**

Solution: Import water objects first:

```bash
python scripts/seed_reference_objects.py
python scripts/seed_passport_texts.py
python rag_agent/scripts/rebuild_vector_store.py
```

**RAG returns no results**

Solution: Check vector store exists:

```bash
ls -la backend/rag_agent/data/vector_store/
# Should contain FAISS index files
```

If empty, rebuild:

```bash
python rag_agent/scripts/rebuild_vector_store.py
```

---

## Complete Import Workflow

**Development (Quick):**

```bash
cd backend
python scripts/seed_reference_objects.py
python scripts/seed_passport_texts.py
python rag_agent/scripts/rebuild_vector_store.py
```

**Production (Full):**

```bash
cd backend

# Step 1: Import OSM data
python scripts/import_osm_water.py

# Step 2: Add reference objects (optional but recommended)
python scripts/seed_reference_objects.py
python scripts/seed_passport_texts.py

# Step 3: Rebuild vector store
python rag_agent/scripts/rebuild_vector_store.py

# Step 4: Verify
curl http://localhost:8000/api/objects?limit=10
```

---

## Data Updates

To update existing data:

1. **Modify objects directly in database:**

   ```sql
   UPDATE water_objects
   SET technical_condition = 2,
       passport_date = '2024-01-15'
   WHERE name = 'Коскол';
   ```

2. **Recalculate priorities:**

   ```python
   from database import SessionLocal
   from models.water_object import WaterObject

   db = SessionLocal()
   objects = db.query(WaterObject).all()
   for obj in objects:
       obj.update_priority()
   db.commit()
   ```

3. **Rebuild vector store after changes:**
   ```bash
   python rag_agent/scripts/rebuild_vector_store.py
   ```

---

## Support

For issues or questions:

1. Check logs: `docker logs promtech-backend-1`
2. Review database: `docker exec -it promtech-db-1 psql -U gidrouser -d gidrodb`
3. Verify migrations: `alembic current`

---

_Last updated: December 2024_
