# Backend Scripts

This directory contains utility scripts for data management and system maintenance.

## Data Import Scripts

### seed_reference_objects.py

Seeds the database with reference water objects from hackathon documentation.

**Usage:**

```bash
python scripts/seed_reference_objects.py
```

**What it does:**

- Inserts 5 reference water objects (Коскол, Камыстыкол, etc.)
- Sets realistic technical conditions and passport dates
- Calculates priorities automatically
- Skips objects that already exist (safe to re-run)

**Output:**

```
======================================================================
Seeding Reference Water Objects
======================================================================
✓ Seeded Коскол (ID: 1, Priority: 11, Level: high)
✓ Seeded Камыстыкол (ID: 2, Priority: 8, Level: medium)
...
======================================================================
Seeded 5 reference objects
======================================================================
```

---

### seed_passport_texts.py

Seeds passport text data for reference water objects.

**Usage:**

```bash
python scripts/seed_passport_texts.py
```

**Prerequisites:**

- Run `seed_reference_objects.py` first

**What it does:**

- Adds detailed passport text for Коскол and Камыстыкол
- Includes geographic, technical, and ecological information
- Stores data in structured sections (general_info, technical_params, ecological_state, recommendations)

**Output:**

```
======================================================================
Seeding Passport Text Data
======================================================================

📄 Seeding passport for Коскол...
  ✓ Seeded passport for Коскол

📄 Seeding passport for Камыстыкол...
  ✓ Seeded passport for Камыстыкол

======================================================================
Total passports seeded: 2
======================================================================
```

---

### seed_all_passports.py

**NEW!** Seeds all passport PDFs from `uploads/passports/` directory.

**Usage:**

```bash
# Test run (parse only, no database insertion)
python scripts/seed_all_passports.py --dry-run

# Full import (insert all passports)
python scripts/seed_all_passports.py
```

**What it does:**

- Scans `uploads/passports/` for all PDF files
- Extracts text from each PDF using pypdf
- Parses metadata: name, region, resource type, coordinates, technical condition, etc.
- Creates WaterObject entries with extracted metadata
- Creates PassportText entries with full text and structured sections
- Calculates priorities automatically
- Links PDFs via `pdf_url` field
- Skips duplicates (safe to re-run)

**Expected results:**

- 20 water objects from passport PDFs
- Includes famous Kazakhstan lakes: Балхаш, Алаколь, Тенгиз, Боровое
- Includes major reservoirs: Капшагайское, Бухтарминское, Шардаринское
- Includes irrigation canals: Иртыш-Караганда, Большой Алматинский

**Output:**

```
======================================================================
Seeding All Passport PDFs
======================================================================
Directory: /backend/uploads/passports
Found 20 PDF files

📄 Processing a1b2c3d4-1234-5678-9abc-def012345001.pdf...
  ✓ Extracted 857 characters
  ✓ Parsed metadata: Озеро Балхаш (Алматинская)
  ✓ Created water object (ID: 6, Priority: 9)
  ✓ Created passport text
...
======================================================================
Processing Complete
======================================================================
Total PDFs: 20
Successfully processed: 20
Failed: 0
======================================================================
Success rate: 100.0%
```

---

### import_osm_water.py

Imports water bodies from OpenStreetMap for Kazakhstan.

**Usage:**

```bash
# Test run (parse only, no database insertion)
python scripts/import_osm_water.py --limit 50 --dry-run

# Import limited number of objects (testing)
python scripts/import_osm_water.py --limit 500

# Full import (all water bodies in Kazakhstan)
python scripts/import_osm_water.py
```

**What it does:**

- Queries Overpass API for Kazakhstan water bodies (lakes, rivers, canals, reservoirs)
- Parses OSM tags into WaterObject format
- Filters for named water bodies only
- Bulk inserts into database in batches of 100
- Handles API rate limits with retry logic

**Expected results:**

- ~1000-5000 water bodies from Kazakhstan
- Takes 5-15 minutes depending on API load
- Region names initially set to "Неизвестная область" (can be enhanced later)

**Options:**

- `--limit N`: Import max N objects (useful for testing)
- `--dry-run`: Parse data but don't insert into database

---

## Documentation

### DATA_IMPORT_GUIDE.md

Comprehensive guide covering:

- Quick start with reference objects
- Large-scale OSM import
- Vector store indexing (required after data import)
- Troubleshooting common issues
- Complete import workflow

**Read this first before running import scripts!**

---

## Quick Start Workflow

**Development (quick setup with real data):**

```bash
cd backend

# Step 1: Seed reference objects (5 objects)
python scripts/seed_reference_objects.py

# Step 2: Seed passport texts for reference objects
python scripts/seed_passport_texts.py

# Step 3: Seed all passport PDFs (20 objects with real data)
python scripts/seed_all_passports.py

# Step 4: Rebuild vector store (REQUIRED)
python rag_agent/scripts/rebuild_vector_store.py
```

**Total after quick setup: 25 water objects, 22 passports**

**Production (full data):**

```bash
cd backend

# Step 1: Seed all passport PDFs (20 real objects)
python scripts/seed_all_passports.py

# Step 2: Import from OSM (1000+ objects)
python scripts/import_osm_water.py

# Step 3: Add reference objects (optional)
python scripts/seed_reference_objects.py
python scripts/seed_passport_texts.py

# Step 4: Rebuild vector store (REQUIRED)
python rag_agent/scripts/rebuild_vector_store.py
```

---

## Docker Usage

If running in Docker, exec into the backend container first:

```bash
# Enter container
docker exec -it promtech-backend-1 bash

# Navigate to backend directory
cd /backend

# Run any script
python scripts/seed_reference_objects.py
```

---

## Verification

After running import scripts, verify data was inserted:

```bash
# Check database
docker exec -it promtech-db-1 psql -U gidrouser -d gidrodb

# SQL queries
SELECT COUNT(*) FROM water_objects;
SELECT name, region, priority, priority_level FROM water_objects LIMIT 5;
SELECT COUNT(*) FROM passport_texts;

# Or use Python
docker exec promtech-backend-1 python3 << EOF
from database import SessionLocal
from models.water_object import WaterObject
from models.passport_text import PassportText

db = SessionLocal()
print(f"Water objects: {db.query(WaterObject).count()}")
print(f"Passports: {db.query(PassportText).count()}")
db.close()
EOF
```

---

## Troubleshooting

**Error: `ModuleNotFoundError: No module named 'database'`**

Solution: Run scripts from backend directory or use absolute imports

**Error: `Connection refused` (database)**

Solution: Ensure PostgreSQL container is running:

```bash
docker-compose ps
docker-compose up -d  # if stopped
```

**Error: `429 Too Many Requests` (OSM import)**

Solution: Overpass API rate limit. Wait 5 minutes and retry.

**Warning: `Parsed 0 valid water objects` (OSM import)**

Solution: Check OSM data exists for region using https://overpass-turbo.eu/

---

## Script Dependencies

All scripts require:

- `sqlalchemy` - Database ORM
- `requests` - HTTP client (OSM import only)
- Database connection via `database.py`
- Models: `WaterObject`, `PassportText`

Dependencies are already in `requirements.txt`.

---

## Notes

1. **Vector Store**: After ANY data import, rebuild the RAG vector store:

   ```bash
   python rag_agent/scripts/rebuild_vector_store.py
   ```

2. **Priority Calculation**: Automatic based on technical_condition and passport_age

3. **Idempotency**: Reference object scripts check for existing data and skip duplicates

4. **OSM Data**: Limited metadata (region names, water types, fauna) - enhance as needed

---

_For detailed information, see [DATA_IMPORT_GUIDE.md](./DATA_IMPORT_GUIDE.md)_
