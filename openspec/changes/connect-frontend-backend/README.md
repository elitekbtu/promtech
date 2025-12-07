# OpenSpec Proposal Created: Connect Frontend with Backend

## ✅ Proposal Status: Ready for Review

The OpenSpec change proposal **`connect-frontend-backend`** has been successfully created and validated.

---

## 📋 Proposal Summary

**Change ID:** `connect-frontend-backend`

**Purpose:** Enable seamless connectivity between the React Native Expo frontend and FastAPI backend across all deployment environments (local development, Docker Compose, and production).

**Type:** New capability (additive, non-breaking)

---

## 📁 Files Created

```
openspec/changes/connect-frontend-backend/
├── proposal.md              ✅ Created - Why, what, impact
├── tasks.md                 ✅ Created - 5 sections, 40+ tasks
├── design.md                ✅ Created - Technical decisions, risks, migration plan
└── specs/
    └── frontend-api-integration/
        └── spec.md          ✅ Created - 11 requirements, 37 scenarios
```

---

## 🎯 Key Changes

### 1. **Frontend Configuration**

- Environment-aware backend URL resolution
- Support for `localhost`, Docker internal network, and production domains
- `EXPO_PUBLIC_BACKEND_URL` environment variable

### 2. **API Service Layer**

- Comprehensive `api-services.ts` for all GidroAtlas endpoints
- Type-safe TypeScript interfaces matching backend Pydantic schemas
- Services for: water objects, priorities, passports, RAG, Face ID

### 3. **Docker Integration**

- Frontend service added to `docker-compose.yml`
- Proper networking between frontend, backend, and postgres
- Hot reload support with volume mounts

### 4. **Authentication Flow**

- JWT token management with SecureStore
- Role-based access control (guest vs expert)
- Token expiration handling

### 5. **Documentation**

- Updated README files
- Troubleshooting guides for CORS, networking, environment variables
- API endpoint documentation

---

## 📊 Validation Results

```bash
✅ openspec validate connect-frontend-backend --strict
   Result: Change 'connect-frontend-backend' is valid
```

**Validation checks passed:**

- ✅ Proposal.md exists with required sections
- ✅ Tasks.md exists with implementation checklist
- ✅ Design.md exists with technical decisions
- ✅ Spec deltas exist in specs/ directory
- ✅ All requirements have at least one scenario
- ✅ Scenario format is correct (#### Scenario: Name)
- ✅ Delta operations properly marked (## ADDED Requirements)

---

## 🔢 Stats

- **Requirements:** 11 new requirements
- **Scenarios:** 37 test scenarios
- **Tasks:** 40+ implementation tasks organized in 5 sections
- **Affected capabilities:** 4 (1 new, 3 existing)
- **Breaking changes:** 0 (fully backwards compatible)

---

## 📝 Requirements Overview

1. **Environment-Aware Backend Configuration** (4 scenarios)
2. **Water Objects API Integration** (4 scenarios)
3. **Priorities API Integration** (3 scenarios)
4. **RAG System API Integration** (3 scenarios)
5. **Face ID Verification API Integration** (3 scenarios)
6. **Authentication Flow Integration** (4 scenarios)
7. **TypeScript Type Definitions** (3 scenarios)
8. **Error Handling and User Feedback** (3 scenarios)
9. **Docker Compose Integration** (4 scenarios)
10. **CORS Configuration** (3 scenarios)
11. **Development Documentation** (3 scenarios)

---

## 🚀 Next Steps

### Before Implementation:

1. **Review Proposal**

   - Read `proposal.md` for high-level overview
   - Review `design.md` for technical decisions
   - Check `tasks.md` for implementation scope

2. **Request Approval**

   - Share proposal with team/stakeholders
   - Address any concerns or questions
   - Get sign-off before starting implementation

3. **Prepare Environment**
   - Ensure Docker and Docker Compose installed
   - Backend running and accessible
   - Node.js 18+ installed for frontend

### During Implementation:

```bash
# Track progress using tasks.md
- [ ] Mark tasks as you complete them
- [ ] Update with any blockers or notes
- [ ] Keep proposal in sync with reality
```

### After Implementation:

```bash
# Archive the change (in a separate PR after deployment)
openspec archive connect-frontend-backend --yes
```

---

## 🔗 Related Files

**Frontend:**

- `frontend/lib/config.ts` - Backend URL configuration
- `frontend/lib/api-services.ts` - New API service layer (to be created)
- `frontend/lib/types.ts` - TypeScript interfaces (to be created)
- `frontend/README.md` - Documentation updates needed

**Backend:**

- `backend/main.py` - CORS configuration may need updates
- `backend/services/auth/router.py` - Authentication endpoints
- `backend/services/objects/router.py` - Water objects API
- `backend/services/priorities/router.py` - Priorities API

**Infrastructure:**

- `docker-compose.yml` - Add frontend service
- `dockerfiles/frontend.Dockerfile` - New Dockerfile needed
- `.env.example` - Add frontend environment variables

---

## 💡 Key Design Decisions

### ✅ Chosen Approaches:

1. **Runtime environment detection** → Flexible, no rebuilds needed
2. **Domain-specific service layer** → Clear, maintainable, testable
3. **Dedicated frontend Docker service** → Clean, secure, scalable
4. **Exact TypeScript schema matching** → Simple, reliable type safety

### ❌ Rejected Alternatives:

1. ~~Separate config files per environment~~ → Hard to maintain
2. ~~Inline fetch calls~~ → Code duplication, hard to test
3. ~~Host network mode~~ → Security concerns
4. ~~camelCase field transformation~~ → Unnecessary complexity

---

## ⚠️ Known Risks & Mitigations

| Risk                           | Mitigation                                                    |
| ------------------------------ | ------------------------------------------------------------- |
| CORS misconfiguration          | Document all origins, test in all environments                |
| Docker networking issues       | Use service names, add healthchecks, document troubleshooting |
| Environment variable confusion | Single source of truth (root .env), clear naming              |
| Bundle size increase           | Accept small increase (<5KB) for type safety benefits         |

---

## 📈 Success Metrics

- [ ] Frontend connects to backend in Docker Compose
- [ ] All API calls return expected data
- [ ] Authentication flow works end-to-end
- [ ] Role-based access control functions correctly
- [ ] Zero CORS errors in browser console
- [ ] New developer setup time < 15 minutes

---

## 🆘 Support & Questions

**Troubleshooting Guide:** See `design.md` section "Risks / Trade-offs"

**Open Questions:** See `design.md` section "Open Questions"

- API retry logic
- Offline support
- Production Dockerfile optimization
- API versioning strategy

---

## ✨ Quick Start Command Reference

```bash
# View the proposal
openspec show connect-frontend-backend

# Validate changes
openspec validate connect-frontend-backend --strict

# List all changes
openspec list

# After implementation and deployment
openspec archive connect-frontend-backend --yes
```

---

**Status:** ✅ **READY FOR REVIEW AND APPROVAL**

**Created:** December 7, 2025
**Validated:** ✅ Pass (strict mode)
**Approval:** ⏳ Pending
