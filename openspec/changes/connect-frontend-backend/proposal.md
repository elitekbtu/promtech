# Change: Connect Frontend with Backend

## Why

The frontend application needs proper integration with all backend API endpoints for water object management, authentication, priorities, and RAG system. Currently, the API integration is incomplete and lacks type safety.

**Current Issues:**

- No proper API service layer for water objects, priorities, and passports
- Authentication flow exists but needs integration testing
- RAG system partially integrated but needs complete endpoint mapping
- No environment-aware configuration for different deployment scenarios (local dev, production)
- Missing TypeScript interfaces for type-safe API calls

## What Changes

### 1. Frontend Configuration

- ✅ Enhance `config.ts` to support multiple backend URLs (localhost, production)
- ✅ Add environment detection (web, native)
- ✅ Update `.env.example` with proper backend URL configurations

### 2. API Service Layer

- ✅ Create comprehensive `api-services.ts` for GidroAtlas endpoints:
  - Water objects (GET list, GET by id, filters, sorting)
  - Priorities (GET table, GET stats) - expert only
  - Passports (GET passport, upload passport)
  - RAG system (query, explain priority, search)
  - Face ID (verify)
- ✅ Replace generic `api-client.ts` references with GidroAtlas-specific services
- ✅ Add TypeScript interfaces matching backend Pydantic schemas

### 3. Backend CORS Configuration

- ✅ Update CORS settings to allow localhost:19006
- ✅ Ensure credentials and preflight requests work correctly

### 4. Authentication Integration

- ✅ Test login/register flows with backend
- ✅ Verify JWT token handling and SecureStore integration
- ✅ Ensure role-based access control (guest vs expert) works correctly
- ✅ Add token refresh mechanism if needed

### 5. Documentation

- ✅ Update frontend README with backend connection instructions
- ✅ Add troubleshooting guide for common connection issues
- ✅ Document environment variable configurations

## Impact

**Affected capabilities:**

- `frontend-api-integration` (new capability)
- `authentication` (existing)
- `rag-system` (existing)

**Affected code:\*\***

- `frontend/lib/config.ts` - Backend URL configuration
- `frontend/lib/api-services.ts` - New comprehensive API service layer
- `frontend/lib/api-client.ts` - Update or deprecate legacy code
- `backend/main.py` - CORS configuration updates
- `.env.example` - Add frontend environment variables
- `frontend/README.md` - Updated connection documentation

**Breaking changes:\*\***

- None - this is additive functionality

**Benefits:**

- ✅ Frontend properly connects to backend in all environments
- ✅ Complete API integration for all GidroAtlas features
- ✅ Type-safe API calls with proper error handling
- ✅ Environment-aware configuration
- ✅ Better developer experience with clear documentation

**Risks:\*\***

- CORS configuration may need adjustment for different environments
- Environment variable management across different deployment scenarios

**Migration path:\*\***

- Existing configurations continue to work (localhost default)
- Gradual migration of legacy API calls to new service layer
