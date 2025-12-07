# Environment Variables Documentation

## Overview

This document describes all environment variables used in the GidroAtlas backend system. Environment variables control database connections, authentication, file storage, AI integration, and operational behavior.

---

## Configuration File

Environment variables are defined in the `.env` file at the project root.

**Create from template:**

```bash
cp env.example .env
```

**File location:**

```
c:\work\promtech\.env
```

---

## Database Configuration

### DATABASE_URL

**Description:** PostgreSQL database connection string

**Required:** ✅ Yes

**Format:** `postgresql://username:password@host:port/database`

**Examples:**

```env
# Docker Compose (default)
DATABASE_URL=postgresql://user:password@postgres:5432/gidroatlas

# Local PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/gidroatlas

# Remote PostgreSQL with SSL
DATABASE_URL=postgresql://user:password@db.example.com:5432/gidroatlas?sslmode=require
```

**Components:**

- `username` — Database user (default: `user`)
- `password` — Database password (default: `password`)
- `host` — Database server hostname (default: `postgres` in Docker, `localhost` for local)
- `port` — PostgreSQL port (default: `5432`)
- `database` — Database name (default: `gidroatlas`)

**Security Notes:**

- ⚠️ **Never commit passwords to git**
- 🔒 Use strong passwords in production (min 16 characters)
- 🔐 Enable SSL for remote connections

---

## Authentication & Security

### SECRET_KEY

**Description:** Secret key for JWT token signing and encryption

**Required:** ✅ Yes

**Format:** String (minimum 32 characters recommended)

**Examples:**

```env
# Development (NOT SECURE - DO NOT USE IN PRODUCTION)
SECRET_KEY=dev-secret-key-not-for-production

# Production (generate random)
SECRET_KEY=a4f8c9e1b7d3e6f2c8a1d5e9b3f7c2a8d4e1b6c9f3a7d2e5c1b8f4a9d6e3c7b1
```

**Generate Secure Key:**

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Security Notes:**

- 🔒 **Must be unique per environment**
- ⚠️ **Changing this invalidates all existing JWT tokens**
- 🔐 Store securely (use secrets manager in production)

---

### ACCESS_TOKEN_EXPIRE_MINUTES

**Description:** JWT token expiration time in minutes

**Required:** ❌ No

**Default:** `1440` (24 hours)

**Format:** Integer (minutes)

**Examples:**

```env
# 24 hours (default)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 8 hours (more secure for production)
ACCESS_TOKEN_EXPIRE_MINUTES=480

# 1 hour (high security environments)
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 7 days (convenience for development)
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

**Recommendations:**

- **Development:** 24 hours (1440 minutes)
- **Production:** 8 hours (480 minutes)
- **High Security:** 1-2 hours (60-120 minutes)

**Trade-offs:**

- Shorter expiration = Better security, more frequent logins
- Longer expiration = Better UX, higher security risk if token compromised

---

## File Storage

### FILE_STORAGE_PATH

**Description:** Local directory path for file uploads (avatars, passport PDFs)

**Required:** ❌ No

**Default:** `uploads`

**Format:** Relative or absolute directory path

**Examples:**

```env
# Relative path (default)
FILE_STORAGE_PATH=uploads

# Absolute path (Linux/Mac)
FILE_STORAGE_PATH=/var/gidroatlas/uploads

# Absolute path (Windows)
FILE_STORAGE_PATH=C:\gidroatlas\uploads

# Docker volume mount
FILE_STORAGE_PATH=/app/uploads
```

**Directory Structure:**

```
uploads/
├── avatars/           # User profile pictures
└── passports/         # Water object passport PDFs
```

**Setup:**

```bash
# Create directories
mkdir -p uploads/avatars
mkdir -p uploads/passports

# Set permissions (Linux/Mac)
chmod -R 755 uploads/
```

**Docker Configuration:**

```yaml
# docker-compose.yml
services:
  backend:
    volumes:
      - ./uploads:/app/uploads
```

---

### FILE_STORAGE_BASE_URL

**Description:** Public base URL for accessing uploaded files

**Required:** ❌ No

**Default:** `/uploads`

**Format:** URL path (relative or absolute)

**Examples:**

```env
# Relative URL (default, served by backend)
FILE_STORAGE_BASE_URL=/uploads

# Absolute URL (CDN)
FILE_STORAGE_BASE_URL=https://cdn.gidroatlas.kz/uploads

# S3-compatible storage
FILE_STORAGE_BASE_URL=https://storage.example.com/gidroatlas
```

**How It Works:**

When a passport PDF is uploaded:

1. File saved to: `{FILE_STORAGE_PATH}/passports/barakkol.pdf`
2. Database stores: `{FILE_STORAGE_BASE_URL}/passports/barakkol.pdf`
3. Frontend requests: `https://gidroatlas.kz/uploads/passports/barakkol.pdf`

**Production Options:**

**Option 1: Backend Serving (Simple)**

```env
FILE_STORAGE_BASE_URL=/uploads
```

- Backend serves files directly
- Easy setup, no external dependencies

**Option 2: Nginx Serving (Better Performance)**

```env
FILE_STORAGE_BASE_URL=/uploads
```

```nginx
# nginx.conf
location /uploads {
    alias /var/gidroatlas/uploads;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Option 3: CDN (Best Performance)**

```env
FILE_STORAGE_BASE_URL=https://cdn.gidroatlas.kz/uploads
```

- Best for high traffic
- Requires CDN setup (CloudFront, Cloudflare, etc.)

---

## AI & Gemini Integration

### GEMINI_API_KEY

**Description:** Google Gemini API key for AI features

**Required:** ✅ Yes (for RAG system)

**Format:** String (API key from Google AI Studio)

**Example:**

```env
GEMINI_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz
```

**Obtain API Key:**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key to `.env` file

**Security Notes:**

- 🔒 **Never commit API key to git**
- 🔐 Restrict key usage by IP/domain in production
- 📊 Monitor API quota and usage

---

### GEMINI_MODEL

**Description:** Gemini model version to use

**Required:** ❌ No

**Default:** `gemini-2.0-flash-exp`

**Format:** Model identifier string

**Available Models:**

```env
# Latest experimental (default, best performance)
GEMINI_MODEL=gemini-2.0-flash-exp

# Stable production version
GEMINI_MODEL=gemini-1.5-pro

# Fast responses, lower cost
GEMINI_MODEL=gemini-1.5-flash

# Legacy (not recommended)
GEMINI_MODEL=gemini-1.0-pro
```

**Model Comparison:**

| Model                | Speed  | Quality  | Cost | Use Case                |
| -------------------- | ------ | -------- | ---- | ----------------------- |
| gemini-2.0-flash-exp | ⚡⚡⚡ | ⭐⭐⭐   | 💰   | Development, testing    |
| gemini-1.5-pro       | ⚡⚡   | ⭐⭐⭐⭐ | 💰💰 | Production, accuracy    |
| gemini-1.5-flash     | ⚡⚡⚡ | ⭐⭐     | 💰   | Production, high volume |

**Recommendations:**

- **Development:** `gemini-2.0-flash-exp` (latest features)
- **Production:** `gemini-1.5-pro` (stable, accurate)
- **High Traffic:** `gemini-1.5-flash` (fast, cost-effective)

---

## CORS Configuration

### CORS_ORIGINS

**Description:** Allowed origins for Cross-Origin Resource Sharing

**Required:** ❌ No

**Default:** `*` (allow all - development only)

**Format:** Comma-separated list of URLs

**Examples:**

```env
# Development (allow all)
CORS_ORIGINS=*

# Production (single domain)
CORS_ORIGINS=https://gidroatlas.kz

# Production (multiple domains)
CORS_ORIGINS=https://gidroatlas.kz,https://www.gidroatlas.kz,https://admin.gidroatlas.kz

# Development + Production
CORS_ORIGINS=http://localhost:8081,http://localhost:3000,https://gidroatlas.kz
```

**Security Best Practices:**

⚠️ **Never use `*` in production!**

✅ **Production Configuration:**

```env
# Whitelist specific domains only
CORS_ORIGINS=https://gidroatlas.kz,https://www.gidroatlas.kz

# No wildcards!
# CORS_ORIGINS=*.gidroatlas.kz  ← WRONG!
```

**Backend Implementation:**

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Logging

### LOG_LEVEL

**Description:** Application logging verbosity

**Required:** ❌ No

**Default:** `INFO`

**Format:** Log level keyword

**Available Levels:**

```env
# Development (verbose)
LOG_LEVEL=DEBUG

# Production (default)
LOG_LEVEL=INFO

# Production (warnings only)
LOG_LEVEL=WARNING

# Critical errors only
LOG_LEVEL=ERROR
```

**Log Level Hierarchy:**

| Level   | Description                         | Use Case               |
| ------- | ----------------------------------- | ---------------------- |
| DEBUG   | Detailed debugging information      | Development, debugging |
| INFO    | General informational messages      | Production (default)   |
| WARNING | Warning messages (potential issues) | Production (minimal)   |
| ERROR   | Error messages (failures)           | Critical systems       |

**Example Log Output:**

```bash
# DEBUG level
2024-01-01 12:00:00 DEBUG [main] Database query: SELECT * FROM water_objects
2024-01-01 12:00:00 DEBUG [auth] JWT token validated for user: expert1
2024-01-01 12:00:00 INFO [api] GET /api/objects - 200 OK

# INFO level
2024-01-01 12:00:00 INFO [api] GET /api/objects - 200 OK
2024-01-01 12:00:00 INFO [auth] User logged in: expert1

# WARNING level
2024-01-01 12:00:00 WARNING [database] Connection pool nearing capacity: 18/20
```

**Recommendations:**

- **Development:** `DEBUG` (see everything)
- **Staging:** `INFO` (moderate detail)
- **Production:** `INFO` or `WARNING` (performance vs visibility)

---

## PostgreSQL Container Configuration

These variables are used by the PostgreSQL Docker container.

### POSTGRES_USER

**Description:** PostgreSQL superuser name

**Required:** ✅ Yes (for Docker)

**Default:** `user`

**Format:** String (alphanumeric, underscores)

**Example:**

```env
POSTGRES_USER=gidroatlas
```

---

### POSTGRES_PASSWORD

**Description:** PostgreSQL superuser password

**Required:** ✅ Yes (for Docker)

**Default:** `password`

**Format:** String

**Example:**

```env
POSTGRES_PASSWORD=SecureP@ssw0rd123!
```

**Security:**

- 🔒 Minimum 16 characters
- 🔐 Include uppercase, lowercase, numbers, symbols
- ⚠️ Never commit to git

---

### POSTGRES_DB

**Description:** Initial database name

**Required:** ✅ Yes (for Docker)

**Default:** `gidroatlas`

**Format:** String (alphanumeric, underscores)

**Example:**

```env
POSTGRES_DB=gidroatlas_prod
```

---

## Complete Example Configuration

### Development (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/gidroatlas
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=gidroatlas

# Security (NOT SECURE - DEVELOPMENT ONLY)
SECRET_KEY=dev-secret-key-not-for-production-use
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Storage
FILE_STORAGE_PATH=uploads
FILE_STORAGE_BASE_URL=/uploads

# AI
GEMINI_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz
GEMINI_MODEL=gemini-2.0-flash-exp

# CORS (allow all for development)
CORS_ORIGINS=*

# Logging
LOG_LEVEL=DEBUG
```

---

### Production (.env.prod)

```env
# Database
DATABASE_URL=postgresql://gidroatlas:Xt9Qp2#mK8vL4$nR@postgres:5432/gidroatlas_prod
POSTGRES_USER=gidroatlas
POSTGRES_PASSWORD=Xt9Qp2#mK8vL4$nR
POSTGRES_DB=gidroatlas_prod

# Security (SECURE - RANDOMLY GENERATED)
SECRET_KEY=a4f8c9e1b7d3e6f2c8a1d5e9b3f7c2a8d4e1b6c9f3a7d2e5c1b8f4a9d6e3c7b1
ACCESS_TOKEN_EXPIRE_MINUTES=480

# File Storage (Absolute path for production)
FILE_STORAGE_PATH=/var/gidroatlas/uploads
FILE_STORAGE_BASE_URL=https://gidroatlas.kz/uploads

# AI
GEMINI_API_KEY=AIzaSyD9876543210zyxwvutsrqponmlkjihgfedcba
GEMINI_MODEL=gemini-1.5-pro

# CORS (Restrict to production domain)
CORS_ORIGINS=https://gidroatlas.kz,https://www.gidroatlas.kz

# Logging
LOG_LEVEL=INFO
```

---

## Validation Checklist

### Before First Run

- [ ] Copy `env.example` to `.env`
- [ ] Set `DATABASE_URL` (check hostname for Docker)
- [ ] Generate strong `SECRET_KEY` (min 32 chars)
- [ ] Set `GEMINI_API_KEY`
- [ ] Create `uploads/avatars` and `uploads/passports` directories
- [ ] Set `CORS_ORIGINS=*` for development

### Before Production Deployment

- [ ] Generate new production `SECRET_KEY`
- [ ] Use strong `POSTGRES_PASSWORD` (16+ chars)
- [ ] Set `CORS_ORIGINS` to your production domain only
- [ ] Set `FILE_STORAGE_PATH` to absolute path
- [ ] Update `FILE_STORAGE_BASE_URL` to production URL
- [ ] Set `ACCESS_TOKEN_EXPIRE_MINUTES=480` (8 hours)
- [ ] Set `LOG_LEVEL=INFO` or `WARNING`
- [ ] Verify `GEMINI_API_KEY` is production key
- [ ] Never commit `.env` to git (check `.gitignore`)

---

## Security Best Practices

### DO ✅

- Use strong passwords (16+ characters)
- Generate random SECRET_KEY for each environment
- Restrict CORS_ORIGINS in production
- Store .env in secure location
- Use environment variable injection in CI/CD
- Rotate secrets periodically
- Enable SSL for database connections
- Use secrets managers in production (AWS Secrets Manager, HashiCorp Vault)

### DON'T ❌

- Commit `.env` to git
- Use default passwords in production
- Use `CORS_ORIGINS=*` in production
- Share API keys publicly
- Reuse SECRET_KEY across environments
- Store secrets in code
- Log sensitive environment variables

---

## Troubleshooting

### Issue: Database Connection Failed

**Symptom:**

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Check:**

```bash
echo $DATABASE_URL
# Verify: correct username, password, hostname, port, database name
```

**Common Fixes:**

- Docker: Use `postgres` as hostname (not `localhost`)
- Local: Use `localhost` as hostname (not `postgres`)
- Check PostgreSQL is running: `docker compose ps postgres`

---

### Issue: JWT Token Invalid

**Symptom:**

```
{"detail": "Could not validate credentials"}
```

**Check:**

```bash
echo $SECRET_KEY
# Should be set and at least 32 characters
```

**Fix:**

- If SECRET_KEY changed, all users must re-login
- Generate new key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

### Issue: File Upload Failed

**Symptom:**

```
FileNotFoundError: [Errno 2] No such file or directory: 'uploads/passports'
```

**Check:**

```bash
echo $FILE_STORAGE_PATH
ls -la uploads/
```

**Fix:**

```bash
mkdir -p uploads/avatars
mkdir -p uploads/passports
chmod -R 755 uploads/
```

---

### Issue: CORS Error in Browser

**Symptom:**

```
Access to fetch at 'http://localhost:8000/api/objects' from origin 'http://localhost:8081'
has been blocked by CORS policy
```

**Check:**

```bash
echo $CORS_ORIGINS
```

**Fix:**

```env
# Add frontend origin
CORS_ORIGINS=http://localhost:8081,http://localhost:3000

# Or allow all (development only)
CORS_ORIGINS=*
```

---

## Environment Variable Loading

### Python (Backend)

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# With default value
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    env_file:
      - .env
```

---

## References

- [Environment Variables Best Practices](https://12factor.net/config)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [CORS Configuration](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

_Last updated: 2024_
