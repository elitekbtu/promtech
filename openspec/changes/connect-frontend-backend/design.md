## Context

The GidroAtlas project has a FastAPI backend and React Native Expo frontend that need to communicate seamlessly across different deployment environments:

1. **Local development**: Backend on `localhost:8000`, frontend on `localhost:19006`
2. **Production**: Backend on custom domain, frontend on custom domain

**Constraints:**

- Must support both web and native (iOS/Android) platforms
- Must maintain security (JWT tokens, CORS)
- Must be backwards compatible with existing local development
- Should follow modular architecture patterns
- Russian language support required for all user-facing content

**Stakeholders:**

- Frontend developers (React Native/Expo)
- Backend developers (FastAPI/Python)
- End users (water resource managers, experts, guests)

## Goals / Non-Goals

**Goals:**

1. Frontend successfully connects to backend in all deployment scenarios
2. Complete type-safe API integration for all GidroAtlas endpoints
3. Seamless authentication and authorization flow
4. Clear documentation for developers

**Non-Goals:\*\***

- Mobile app store deployment (out of scope for this change)
- Production hosting setup (separate concern)
- Backend API modifications (use existing endpoints)
- UI/UX redesign (focus on connectivity only)
- Performance optimization (separate effort)

## Decisions

### Decision 1: Environment-Aware Configuration

**What:** Implement dynamic backend URL resolution based on runtime environment

**Why:**

- Single codebase works in all environments
- No manual configuration changes needed
- Follows Expo best practices for environment variables

**Implementation:**

```typescript
// frontend/lib/config.ts
export function getBackendURL(): string {
  // Priority: env var → Expo config → localhost default
  if (process.env.EXPO_PUBLIC_BACKEND_URL) {
    return process.env.EXPO_PUBLIC_BACKEND_URL;
  }

  // Default to localhost
  return "http://localhost:8000";
}
```

**Alternatives considered:**

- ❌ Separate config files per environment → harder to maintain
- ❌ Build-time configuration → requires rebuilds for environment changes
- ✅ Runtime environment variables → flexible, follows 12-factor app principles

### Decision 2: Comprehensive API Service Layer

**What:** Create unified `api-services.ts` with all GidroAtlas endpoints

**Why:**

- Type safety with TypeScript interfaces
- Single source of truth for API calls
- Easy to mock for testing
- Consistent error handling

**Structure:**

```typescript
// frontend/lib/api-services.ts
export const waterObjectsAPI = {
  list: (filters?: WaterObjectFilters) => Promise<WaterObjectList>,
  getById: (id: number) => Promise<WaterObject>,
  // ...
};

export const prioritiesAPI = {
  getTable: (filters?: PriorityFilters) => Promise<PriorityTable>,
  getStats: () => Promise<PriorityStatistics>,
  // ...
};
```

**Alternatives considered:**

- ❌ Inline fetch calls in components → code duplication, hard to test
- ❌ Keep existing generic `api-client.ts` → doesn't match GidroAtlas domain
- ✅ Domain-specific service layer → clear, maintainable, testable

### Decision 3: TypeScript Interface Parity

**What:** Create TypeScript interfaces matching backend Pydantic schemas exactly

**Why:**

- Compile-time type checking
- Auto-completion in IDEs
- Prevents runtime errors from API changes

**Implementation:**

- Copy enum values from backend (in Russian)
- Match field names exactly (snake_case from API)
- Add optional fields where backend allows nulls

**Alternatives considered:**

- ❌ camelCase conversion → mismatch with API, extra transformation layer
- ❌ `any` types → no type safety
- ✅ Exact schema matching → simple, reliable, maintainable

## Risks / Trade-offs

### Risk: CORS Configuration Complexity

**Risk:** Different environments require different CORS origins, easy to misconfigure

**Impact:** Frontend blocked from accessing backend, cryptic browser errors

**Mitigation:**

- Document all CORS origins in backend `main.py`
- Add CORS troubleshooting section to documentation
- Use wildcard `*` in development, restrict in production
- Test CORS in local and production environments before deployment

### Risk: Environment Variable Management

**Risk:** Multiple `.env` files (root, frontend) can lead to confusion

**Impact:** Wrong backend URL used, services don't connect

**Mitigation:**

- Single source of truth: root `.env` file
- Frontend reads `EXPO_PUBLIC_BACKEND_URL` only
- Clear naming conventions (`EXPO_PUBLIC_` prefix)
- Document in both README files

### Trade-off: Bundle Size vs Type Safety

**Trade-off:** TypeScript interfaces increase bundle size slightly but provide type safety

**Decision:** Accept small bundle increase (< 5KB) for type safety benefits

**Rationale:**

- Type errors caught at compile time save debugging time
- Better developer experience with auto-completion
- Minimal impact on app performance

## Migration Plan

### Phase 1: Configuration Update (Non-Breaking)

1. Update `config.ts` with environment detection
2. Add `EXPO_PUBLIC_BACKEND_URL` to `.env.example`
3. Existing `localhost` default continues to work

### Phase 2: API Service Layer (Additive)

1. Create new `api-services.ts` with all endpoints
2. Add TypeScript interfaces to `types.ts`
3. Legacy `api-client.ts` remains functional
4. Gradually migrate components to new service layer

### Phase 3: Testing & Documentation

1. Test all API endpoints in local environment
2. Update README files with instructions
3. Add troubleshooting guides
4. Validate with fresh setup on new machine

### Rollback Strategy

If issues arise:

1. Revert `config.ts` changes
2. Continue using `localhost` default
3. No impact on backend or database

### Success Metrics

- [ ] Frontend successfully connects to backend locally
- [ ] All API calls return expected data (water objects, priorities, RAG)
- [ ] Authentication flow works end-to-end (register → login → JWT → API calls)
- [ ] Role-based access control functions correctly (guest vs expert)
- [ ] Zero CORS errors in browser console
- [ ] Documentation enables new developer to set up in < 15 minutes

## Open Questions

1. **Question:** Should we add API request retry logic for network failures?

   - **Decision needed by:** Implementation phase
   - **Context:** Mobile networks can be unreliable

2. **Question:** Do we need offline support for water object data?

   - **Decision needed by:** Future enhancement
   - **Context:** Field inspections may have poor connectivity

3. **Question:** How to handle backend API version changes?
   - **Decision needed by:** Before breaking backend changes
   - **Context:** May need API versioning strategy (`/api/v1/`, `/api/v2/`)
