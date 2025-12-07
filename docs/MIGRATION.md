# GidroAtlas Migration and Deployment Guide

## Overview

This guide covers deploying GidroAtlas from development to production environments, including database migrations, data import, and configuration management.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Production Deployment](#production-deployment)
3. [Database Migrations](#database-migrations)
4. [Data Import](#data-import)
5. [Environment Configuration](#environment-configuration)
6. [Backup and Restore](#backup-and-restore)
7. [Rollback Procedures](#rollback-procedures)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum Hardware:**

- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB
- Network: 1Gbps

**Recommended Hardware:**

- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ SSD
- Network: 1Gbps+

**Software:**

- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+ (if not using Docker)
- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)

---

## Production Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/gidroatlas.git
cd gidroatlas
```

### Step 2: Configure Environment

Create production `.env` file:

```bash
cp env.example .env
nano .env
```

**Critical Production Settings:**

```env
# Database
DATABASE_URL=postgresql://gidroatlas:STRONG_PASSWORD@postgres:5432/gidroatlas_prod

# Security
SECRET_KEY=GENERATE_RANDOM_32_CHAR_STRING_HERE
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS (Restrict to your domain)
CORS_ORIGINS=https://gidroatlas.kz,https://www.gidroatlas.kz

# File Storage
FILE_STORAGE_PATH=/var/gidroatlas/uploads
FILE_STORAGE_BASE_URL=https://gidroatlas.kz/uploads

# AI
GEMINI_API_KEY=your-production-gemini-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Logging
LOG_LEVEL=INFO
```

**Generate SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Build Docker Images

```bash
docker compose -f docker-compose.prod.yml build
```

**Production docker-compose.prod.yml:**

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: gidroatlas_prod
      POSTGRES_USER: gidroatlas
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    restart: always

  backend:
    build:
      context: .
      dockerfile: dockerfiles/backend.Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
    volumes:
      - uploads_prod:/var/gidroatlas/uploads
    depends_on:
      - postgres
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: ../dockerfiles/frontend.Dockerfile
    ports:
      - "80:8081"
      - "443:8081"
    depends_on:
      - backend
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - uploads_prod:/var/gidroatlas/uploads:ro
    depends_on:
      - backend
      - frontend
    restart: always

volumes:
  postgres_data_prod:
  uploads_prod:
```

### Step 4: Start Services

```bash
docker compose -f docker-compose.prod.yml up -d
```

### Step 5: Verify Deployment

```bash
# Check container status
docker compose -f docker-compose.prod.yml ps

# Check backend logs
docker compose -f docker-compose.prod.yml logs backend

# Test API health
curl https://gidroatlas.kz/api/health

# Test OpenAPI docs
curl https://gidroatlas.kz/docs
```

---

## Database Migrations

### Initial Setup

**Apply all migrations:**

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

**Check current version:**

```bash
docker compose -f docker-compose.prod.yml exec backend alembic current
```

### Migration History

**Current Migrations:**

1. **`933ade9f4842_add_water_management_models.py`** (Phase 1-8)

   - Creates `users`, `water_objects`, `passport_texts` tables
   - Sets up enums (with English values initially)
   - Adds indexes and constraints

2. **`1d4a14dd5c28_convert_enum_values_to_russian.py`** (Phase 9)
   - Converts all enum values from English to Russian
   - Reversible downgrade available
   - Updates: resource_type, water_type, fauna, priority_level

### Creating New Migrations

**Auto-generate migration:**

```bash
# From backend directory
alembic revision --autogenerate -m "Add new column to water_objects"
```

**Manual migration:**

```bash
alembic revision -m "Custom migration"
```

**Edit migration file:**

```python
# backend/alembic/versions/XXXX_description.py

def upgrade():
    op.add_column('water_objects', sa.Column('new_field', sa.String(), nullable=True))

def downgrade():
    op.drop_column('water_objects', 'new_field')
```

**Apply migration:**

```bash
alembic upgrade head
```

### Migration Best Practices

1. **Always test migrations in staging first**
2. **Create backup before migration**
3. **Ensure migrations are reversible**
4. **Avoid data loss operations**
5. **Test rollback procedures**

### Rolling Back Migrations

**Rollback last migration:**

```bash
alembic downgrade -1
```

**Rollback to specific version:**

```bash
alembic downgrade 933ade9f4842
```

**Rollback all:**

```bash
alembic downgrade base
```

---

## Data Import

### Phase 1: Import Water Objects

**Script:** `backend/scripts/import_objects.py`

```bash
docker compose exec backend python scripts/import_objects.py
```

**What it does:**

- Reads from `backend/data/water_objects.csv`
- Imports 25 water objects
- Sets initial coordinates, types, characteristics
- Calculates initial priorities

**Expected Output:**

```
Importing water objects...
✓ Imported: Бараккол (озеро, Улытауская область)
✓ Imported: Коскол (озеро, Улытауская область)
...
Total: 25 objects imported
```

### Phase 2: Import Passport Documents

**Script:** `backend/scripts/import_passports.py`

```bash
docker compose exec backend python scripts/import_passports.py
```

**What it does:**

- Copies PDF files to `uploads/passports/`
- Creates `pdf_url` references in database
- Extracts text content to `passport_texts` table
- Sets up vector embeddings for RAG

**Expected Output:**

```
Importing passport documents...
✓ Uploaded: barakkol.pdf → /uploads/passports/barakkol.pdf
✓ Extracted text: 1250 words
...
Total: 22 passports imported (88% coverage)
```

### Phase 3: Enrich Data

**Script:** `backend/scripts/enrich_data.py`

```bash
docker compose exec backend python scripts/enrich_data.py
```

**What it does:**

- Updates coordinates with accurate geospatial data
- Fills in missing metadata (area, depth)
- Validates data quality
- Recalculates priorities

**Expected Output:**

```
Enriching water object data...
✓ Updated Бараккол: coordinates, area_ha, depth_m
✓ Updated Коскол: coordinates, area_ha
...
Null values: 0% (all critical fields filled)
Priority distribution: 17 HIGH, 6 MEDIUM, 2 LOW
```

### Custom Data Import

**CSV Format:**

```csv
name,region,resource_type,water_type,fauna,passport_date,technical_condition,latitude,longitude,area_ha,depth_m
"Бараккол","Улытауская область","озеро","непресная","рыбопродуктивная","2015-03-15",5,49.3147,67.2756,1250.5,3.2
```

**Import Custom CSV:**

```python
import pandas as pd
from sqlalchemy.orm import Session
from models.water_object import WaterObject

df = pd.read_csv('custom_objects.csv')

with Session(engine) as session:
    for _, row in df.iterrows():
        obj = WaterObject(
            name=row['name'],
            region=row['region'],
            resource_type=row['resource_type'],
            # ... map all fields
        )
        session.add(obj)
    session.commit()
```

---

## Environment Configuration

### Development vs Production

**Development (`.env`):**

```env
DATABASE_URL=postgresql://user:password@localhost:5432/gidroatlas_dev
SECRET_KEY=dev-secret-key-not-secure
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=*
LOG_LEVEL=DEBUG
```

**Production (`.env.prod`):**

```env
DATABASE_URL=postgresql://gidroatlas:${STRONG_PWD}@postgres:5432/gidroatlas_prod
SECRET_KEY=${GENERATED_SECRET_32_CHARS}
ACCESS_TOKEN_EXPIRE_MINUTES=480
CORS_ORIGINS=https://gidroatlas.kz
LOG_LEVEL=INFO
```

### Environment Variables Reference

See [Environment Variables Documentation](ENV_VARS.md) for complete reference.

**Critical Variables:**

| Variable                    | Required | Description                                |
| --------------------------- | -------- | ------------------------------------------ |
| DATABASE_URL                | Yes      | PostgreSQL connection string               |
| SECRET_KEY                  | Yes      | JWT signing key (min 32 chars)             |
| GEMINI_API_KEY              | Yes      | Google Gemini API key                      |
| CORS_ORIGINS                | Yes      | Allowed frontend origins                   |
| FILE_STORAGE_PATH           | No       | Upload directory (default: uploads)        |
| FILE_STORAGE_BASE_URL       | No       | Public URL for uploads (default: /uploads) |
| ACCESS_TOKEN_EXPIRE_MINUTES | No       | JWT expiration (default: 1440 = 24h)       |

---

## Backup and Restore

### Database Backup

**Full backup:**

```bash
docker compose exec postgres pg_dump -U gidroatlas gidroatlas_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Compressed backup:**

```bash
docker compose exec postgres pg_dump -U gidroatlas gidroatlas_prod | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Automated daily backups (cron):**

```bash
0 2 * * * /usr/local/bin/backup-gidroatlas.sh
```

**backup-gidroatlas.sh:**

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/gidroatlas"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
docker compose -f /opt/gidroatlas/docker-compose.prod.yml exec -T postgres \
  pg_dump -U gidroatlas gidroatlas_prod | gzip > "${BACKUP_DIR}/db_${DATE}.sql.gz"

# Keep only last 30 days
find "${BACKUP_DIR}" -name "db_*.sql.gz" -mtime +30 -delete
```

### File Storage Backup

**Backup uploads directory:**

```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

**Sync to S3:**

```bash
aws s3 sync uploads/ s3://gidroatlas-backups/uploads/ --delete
```

### Database Restore

**Restore from backup:**

```bash
# Stop backend
docker compose stop backend

# Restore database
gunzip < backup_20240101_120000.sql.gz | \
  docker compose exec -T postgres psql -U gidroatlas gidroatlas_prod

# Start backend
docker compose start backend
```

**Restore to new database:**

```bash
# Create new database
docker compose exec postgres createdb -U gidroatlas gidroatlas_restored

# Restore data
gunzip < backup.sql.gz | \
  docker compose exec -T postgres psql -U gidroatlas gidroatlas_restored
```

---

## Rollback Procedures

### Application Rollback

**Rollback to previous version:**

```bash
# Pull previous version
git checkout v1.2.0

# Rebuild containers
docker compose -f docker-compose.prod.yml build

# Stop current version
docker compose -f docker-compose.prod.yml down

# Start previous version
docker compose -f docker-compose.prod.yml up -d
```

### Database Rollback

**Rollback last migration:**

```bash
docker compose exec backend alembic downgrade -1
```

**Rollback specific migration:**

```bash
# Find current version
docker compose exec backend alembic current

# Rollback to previous
docker compose exec backend alembic downgrade 933ade9f4842
```

### Full System Rollback

**Emergency rollback procedure:**

1. **Stop all services:**

```bash
docker compose -f docker-compose.prod.yml down
```

2. **Restore database backup:**

```bash
gunzip < backup_latest.sql.gz | \
  docker compose exec -T postgres psql -U gidroatlas gidroatlas_prod
```

3. **Restore file storage:**

```bash
tar -xzf uploads_backup_latest.tar.gz
```

4. **Checkout previous version:**

```bash
git checkout tags/v1.2.0
```

5. **Restart services:**

```bash
docker compose -f docker-compose.prod.yml up -d
```

6. **Verify:**

```bash
curl https://gidroatlas.kz/api/health
```

---

## Monitoring

### Application Monitoring

**Check service status:**

```bash
docker compose ps
```

**View logs:**

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

**Resource usage:**

```bash
docker stats
```

### Database Monitoring

**Connection count:**

```sql
SELECT count(*) FROM pg_stat_activity;
```

**Database size:**

```sql
SELECT pg_size_pretty(pg_database_size('gidroatlas_prod'));
```

**Table sizes:**

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Slow queries:**

```sql
SELECT
    query,
    calls,
    total_time / 1000 AS total_seconds,
    mean_time / 1000 AS mean_seconds
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### Health Checks

**API Health Endpoint:**

```bash
curl https://gidroatlas.kz/api/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Alerting

**Setup monitoring (recommended):**

- **Prometheus** — Metrics collection
- **Grafana** — Visualization
- **AlertManager** — Alerting

**Key metrics to monitor:**

- API response time
- Database connection pool
- Disk usage
- Memory usage
- Error rate (5xx responses)

---

## Troubleshooting

### Common Issues

#### Issue 1: Database Connection Failed

**Symptom:**

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check connection string
echo $DATABASE_URL

# Restart database
docker compose restart postgres

# Check PostgreSQL logs
docker compose logs postgres
```

#### Issue 2: Migration Failed

**Symptom:**

```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**

```bash
# Check current version
alembic current

# Check migration history
alembic history

# Stamp database with current version
alembic stamp head

# Or rollback and re-apply
alembic downgrade -1
alembic upgrade head
```

#### Issue 3: File Upload Failed

**Symptom:**

```
FileNotFoundError: [Errno 2] No such file or directory: '/uploads/passports'
```

**Solution:**

```bash
# Create upload directories
mkdir -p uploads/passports
mkdir -p uploads/avatars

# Set permissions
chmod -R 755 uploads/

# In Docker, ensure volume is mounted
docker compose down
docker compose up -d
```

#### Issue 4: JWT Token Invalid

**Symptom:**

```
{"detail": "Could not validate credentials"}
```

**Solution:**

```bash
# Verify SECRET_KEY is set
echo $SECRET_KEY

# If changed, users must re-login
# Clear old tokens from frontend

# Check token expiration
# Default: 24 hours (ACCESS_TOKEN_EXPIRE_MINUTES=1440)
```

#### Issue 5: Russian Enum Values Not Showing

**Symptom:**
API returns `resource_type: "lake"` instead of `"озеро"`

**Solution:**

```bash
# Check migration was applied
docker compose exec backend alembic current

# Should show: 1d4a14dd5c28 (head)

# If not, apply migration
docker compose exec backend alembic upgrade 1d4a14dd5c28

# Restart backend
docker compose restart backend
```

### Debug Mode

**Enable debug logging:**

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart backend
docker compose restart backend

# View detailed logs
docker compose logs -f backend
```

### Database Connection Debugging

```python
# Test database connection (Python)
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://user:pass@localhost:5432/gidroatlas"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✓ Database connected successfully")
except OperationalError as e:
    print(f"✗ Database connection failed: {e}")
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Review all code changes
- [ ] Run all tests (`python scripts/run_all_tests.py`)
- [ ] Update version number
- [ ] Create git tag (`git tag v1.0.0`)
- [ ] Backup production database
- [ ] Backup production file storage
- [ ] Review environment variables
- [ ] Generate new SECRET_KEY for production
- [ ] Update CORS_ORIGINS to production domain

### Deployment

- [ ] Pull latest code
- [ ] Build Docker images
- [ ] Apply database migrations
- [ ] Start services
- [ ] Verify health endpoint
- [ ] Test API endpoints
- [ ] Test frontend access
- [ ] Check logs for errors

### Post-Deployment

- [ ] Monitor logs for 30 minutes
- [ ] Run smoke tests
- [ ] Verify priority calculations
- [ ] Test RAG system
- [ ] Verify file uploads work
- [ ] Check database connections
- [ ] Update documentation
- [ ] Notify team of deployment

---

## Contact

For deployment support:

- DevOps Team: devops@gidroatlas.kz
- Technical Lead: tech@gidroatlas.kz
- Emergency: +7 XXX XXX XXXX

---

_Last updated: 2024_
