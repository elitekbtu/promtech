## 1. Frontend Configuration

- [x] 1.1 Update `frontend/lib/config.ts`

  - [x] 1.1.1 Backend URL is already resolved via `getBackendURL()` - verify it works
  - [x] 1.1.2 Ensure `EXPO_PUBLIC_BACKEND_URL` environment variable is supported
  - [x] 1.1.3 Test with localhost and production URLs

- [x] 1.2 Update environment configuration
  - [x] 1.2.1 Update `frontend/.env.example` with backend URL options
  - [x] 1.2.2 Document environment variables in frontend README

## 2. API Service Layer

- [x] 2.1 Create `frontend/lib/api-services.ts`

  - [x] 2.1.1 Add water objects API service
    - [x] GET `/api/objects` with filters (region, type, water_type, fauna, etc.)
    - [x] GET `/api/objects/{id}` for single object details
    - [x] Add TypeScript interfaces for `WaterObject`, `WaterObjectList`
  - [x] 2.1.2 Add priorities API service (expert only)
    - [x] GET `/api/priorities/table` with filters
    - [x] GET `/api/priorities/stats` for statistics
    - [x] Add TypeScript interfaces for `PriorityTable`, `PriorityStats`
  - [x] 2.1.3 Add passports API service
    - [x] GET `/api/passports/{object_id}` for passport metadata
    - [x] POST `/api/passports/upload` for document upload (expert only)
    - [x] Add TypeScript interfaces for `PassportMetadata`
  - [x] 2.1.4 Add RAG system API service
    - [x] POST `/api/rag/query` for natural language queries
    - [x] POST `/api/rag/explain-priority/{id}` for priority explanations
    - [x] Add TypeScript interfaces for `RAGQuery`, `RAGResponse`
  - [x] 2.1.5 Add Face ID API service
    - [x] POST `/api/faceid/verify` for face verification
    - [x] Add TypeScript interfaces for `FaceVerifyRequest`, `FaceVerifyResponse`

- [x] 2.2 Update authentication service

  - [x] 2.2.1 Verify `frontend/lib/auth.ts` works with backend `/api/auth/login`
  - [x] 2.2.2 Test JWT token storage and retrieval
  - [x] 2.2.3 Implement logout functionality (clear tokens and redirect)
  - [x] 2.2.4 Add token refresh mechanism if needed
  - [x] 2.2.5 Verify role-based access (guest vs expert)

- [x] 2.3 Add TypeScript type definitions
  - [x] 2.3.1 Create `frontend/lib/gidroatlas-types.ts` with all API response types
  - [x] 2.3.2 Match Pydantic schemas from backend
  - [x] 2.3.3 Add enums for ResourceType, WaterType, FaunaType, PriorityLevel

## 3. Testing & Validation

- [ ] 3.1 Test authentication flow

  - [ ] 3.1.1 Register new user via frontend → backend
  - [ ] 3.1.2 Login with credentials
  - [ ] 3.1.3 Verify JWT token storage
  - [ ] 3.1.4 Test role-based access (guest cannot see priorities)

- [ ] 3.2 Test water objects API

  - [ ] 3.2.1 Fetch water objects list
  - [ ] 3.2.2 Apply filters (region, type, water type)
  - [ ] 3.2.3 Fetch single object details
  - [ ] 3.2.4 Verify data rendering on map

- [ ] 3.3 Test priorities API (expert only)

  - [ ] 3.3.1 Fetch priority table
  - [ ] 3.3.2 Fetch priority statistics
  - [ ] 3.3.3 Verify guest users cannot access

- [ ] 3.4 Test RAG system

  - [ ] 3.4.1 Send query to RAG endpoint
  - [ ] 3.4.2 Request priority explanation
  - [ ] 3.4.3 Verify responses in Russian

- [ ] 3.5 Test Face ID verification
  - [ ] 3.5.1 Capture photo from frontend
  - [ ] 3.5.2 Send to backend for verification
  - [ ] 3.5.3 Handle success/failure responses

## 4. Documentation

- [x] 4.1 Update `frontend/README.md`

  - [x] 4.1.1 Add backend connection section
  - [x] 4.1.2 Document environment variables
  - [x] 4.1.3 Add troubleshooting guide

- [x] 4.2 Update main `README.md`

  - [x] 4.2.1 Add full-stack setup instructions
  - [x] 4.2.2 Add architecture diagram with frontend

- [x] 4.3 Create troubleshooting guide
  - [x] 4.3.1 CORS errors
  - [x] 4.3.2 Backend connection refused
  - [x] 4.3.3 Environment variable issues
