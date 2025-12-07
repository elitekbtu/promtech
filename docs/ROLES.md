# Role-Based Access Control (RBAC) Documentation

## Overview

GidroAtlas implements a two-tier role system to control access to sensitive water resource data and priority information.

## Role Definitions

### Guest (Гость)

**Purpose:** Public access for general viewing of water resource data

**Permissions:**

- ✅ View water objects on map
- ✅ View basic object information (name, location, type, characteristics)
- ✅ Access RAG system for general queries
- ✅ Use Face ID verification
- ❌ **Cannot see priority scores or levels**
- ❌ **Cannot access prioritization table**
- ❌ **Cannot access priority statistics**
- ❌ **Cannot upload passport documents**
- ❌ **Cannot get AI priority explanations**

**Use Cases:**

- Public officials viewing infrastructure
- Citizens checking local water resources
- Educational purposes
- General research

---

### Expert (Эксперт)

**Purpose:** Full access for water resource management professionals

**Permissions:**

- ✅ All Guest permissions
- ✅ **View priority scores and priority levels**
- ✅ **Access prioritization dashboard**
- ✅ **View priority statistics**
- ✅ **Upload passport documents**
- ✅ **Get AI-powered priority explanations**
- ✅ Filter and sort by priority
- ✅ Export priority reports

**Use Cases:**

- Government water resource managers
- Infrastructure engineers
- Environmental scientists
- Policy makers
- Inspection teams

---

## API Endpoint Access Matrix

| Endpoint                           | Guest | Expert | Notes                                   |
| ---------------------------------- | ----- | ------ | --------------------------------------- |
| **Authentication**                 |       |        |                                         |
| POST /api/auth/login               | ✅    | ✅     | Anyone can authenticate                 |
| POST /api/auth/register            | ✅    | ✅     | Self-registration allowed               |
| **Water Objects**                  |       |        |                                         |
| GET /api/objects                   | ✅ \* | ✅     | \* Guest doesn't see priority fields    |
| GET /api/objects/{id}              | ✅ \* | ✅     | \* Guest doesn't see priority fields    |
| **Priorities**                     |       |        |                                         |
| GET /api/priorities/table          | ❌    | ✅     | Expert only - full prioritization table |
| GET /api/priorities/stats          | ❌    | ✅     | Expert only - statistics dashboard      |
| **Passports**                      |       |        |                                         |
| POST /api/passports/upload         | ❌    | ✅     | Expert only - document management       |
| GET /api/passports/{id}            | ✅    | ✅     | Anyone can view if object is visible    |
| **RAG System**                     |       |        |                                         |
| POST /api/rag/query                | ✅    | ✅     | Both roles, but expert gets more detail |
| GET /api/rag/explain-priority/{id} | ❌    | ✅     | Expert only - priority explanations     |
| **Face ID**                        |       |        |                                         |
| POST /api/faceid/verify            | ✅    | ✅     | Both roles for security                 |

---

## Field-Level Access Control

### Water Objects

When a **Guest** queries `/api/objects` or `/api/objects/{id}`, the response **excludes** priority-related fields:

**Guest Response:**

```json
{
  "id": 1,
  "name": "Бараккол",
  "region": "Улытауская область",
  "resource_type": "озеро",
  "water_type": "непресная",
  "fauna": "рыбопродуктивная",
  "passport_date": "2015-03-15",
  "technical_condition": 5,
  "latitude": 49.3147,
  "longitude": 67.2756,
  "pdf_url": "/uploads/passports/barakkol.pdf",
  "area_ha": 1250.5,
  "depth_m": 3.2
}
```

**Expert Response:**

```json
{
  "id": 1,
  "name": "Бараккол",
  "region": "Улытауская область",
  "resource_type": "озеро",
  "water_type": "непресная",
  "fauna": "рыбопродуктивная",
  "passport_date": "2015-03-15",
  "technical_condition": 5,
  "latitude": 49.3147,
  "longitude": 67.2756,
  "pdf_url": "/uploads/passports/barakkol.pdf",
  "priority": 14,
  "priority_level": "высокий",
  "area_ha": 1250.5,
  "depth_m": 3.2
}
```

**Excluded Fields for Guest:**

- `priority` — Integer priority score
- `priority_level` — Text priority level (высокий/средний/низкий)

---

## Authentication Flow

### 1. Login

**Request:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"expert1","password":"secret123"}'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "expert"
}
```

### 2. Using JWT Token

Include the token in subsequent requests:

```bash
curl http://localhost:8000/api/priorities/table \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. JWT Token Structure

```json
{
  "sub": "expert1",
  "role": "expert",
  "exp": 1735689600
}
```

**Token Contents:**

- `sub` — User's login
- `role` — User's role (`guest` or `expert`)
- `exp` — Token expiration timestamp

---

## Backend Implementation

### Role Enforcement

**Decorator-Based Protection:**

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

def require_expert(token: str = Depends(security)):
    """Require expert role for endpoint access"""
    payload = decode_jwt(token.credentials)
    if payload.get("role") != "expert":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: expert role required"
        )
    return payload

# Usage in routes
@app.get("/api/priorities/table")
def get_priority_table(user: dict = Depends(require_expert)):
    # This endpoint only accessible to experts
    ...
```

**Response Filtering:**

```python
def get_water_object(id: int, token: Optional[str] = None):
    """Get water object with role-based field filtering"""
    obj = db.query(WaterObject).filter_by(id=id).first()

    # Check if user is expert
    is_expert = False
    if token:
        payload = decode_jwt(token)
        is_expert = payload.get("role") == "expert"

    # Build response based on role
    response = {
        "id": obj.id,
        "name": obj.name,
        "region": obj.region,
        # ... basic fields ...
    }

    # Add priority fields only for experts
    if is_expert:
        response["priority"] = obj.priority
        response["priority_level"] = obj.priority_level

    return response
```

---

## Role Assignment

### Default Roles

**New Users:** When registering, users specify their desired role:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "login": "newuser",
    "password": "password123",
    "role": "guest"
  }'
```

**Role Options:**

- `guest` — Default for public users
- `expert` — Requires approval (implementation-dependent)

### Role Management

**Manual Assignment (Database):**

```sql
-- Promote user to expert
UPDATE users
SET role = 'expert'
WHERE login = 'username';

-- Demote user to guest
UPDATE users
SET role = 'guest'
WHERE login = 'username';
```

**Future Enhancement:** Admin panel for role management

---

## Security Considerations

### Why Two Roles?

1. **Data Sensitivity:** Priority information reveals infrastructure vulnerabilities
2. **Regulatory Compliance:** Sensitive government data access tracking
3. **Public Transparency:** General data available to public, sensitive data restricted
4. **Operational Security:** Limit exposure of critical infrastructure assessments

### Role Verification

**Backend verifies role on every request:**

- ✅ JWT token validated
- ✅ Role extracted from token payload
- ✅ Role checked against endpoint requirements
- ✅ Response fields filtered based on role

**Frontend role handling:**

- JWT token stored securely
- Role displayed in UI
- Role-specific features shown/hidden
- Graceful degradation for guests

---

## Migration from Old System

### Previous Roles

If migrating from an older system with different roles:

**Old Roles:**

- `admin` → Maps to `expert`
- `user` → Maps to `guest`

**Migration Script:**

```sql
-- Update old role names to new ones
UPDATE users
SET role = 'expert'
WHERE role = 'admin';

UPDATE users
SET role = 'guest'
WHERE role = 'user';
```

---

## Testing Role-Based Access

### Test Script: `test_rbac.py`

Located at `backend/scripts/test_rbac.py`

**Tests:**

1. Login as guest and expert
2. Verify guest can access `/api/objects` (without priority fields)
3. Verify expert can access `/api/objects` (with priority fields)
4. Verify guest gets 403 on `/api/priorities/table`
5. Verify expert can access `/api/priorities/table`
6. Verify guest gets 403 on `/api/priorities/stats`
7. Verify expert can access `/api/priorities/stats`

**Run Tests:**

```bash
cd backend/scripts
python test_rbac.py
```

---

## Common Scenarios

### Scenario 1: Public Citizen Viewing Local Lake

**User Type:** Guest (not logged in or logged in as guest)

**Actions:**

1. Opens map in frontend
2. Browses to local region
3. Clicks on lake marker
4. Views basic information: name, type, water characteristics, location
5. Can view passport PDF if available
6. **Cannot see** priority score or inspection priority level

**Why:** Priority information is sensitive government data

---

### Scenario 2: Government Engineer Planning Inspections

**User Type:** Expert (logged in with expert credentials)

**Actions:**

1. Logs in with expert account
2. Opens prioritization dashboard (`/api/priorities/table`)
3. Views all objects sorted by priority (highest first)
4. Filters by region: "Улытауская область"
5. Sees priority scores and levels for all objects
6. Queries RAG system: "Почему у озера Бараккол высокий приоритет?"
7. Gets detailed AI explanation with references to passport data
8. Downloads priority report for inspection planning

**Why:** Expert has full access to all priority and management features

---

### Scenario 3: Researcher Analyzing Water Quality

**User Type:** Guest with API access

**Actions:**

1. Authenticates as guest
2. Queries `/api/objects?water_type=пресная&region=Акмолинская область`
3. Gets list of fresh water objects in region
4. Downloads basic data for analysis
5. Uses RAG system to ask: "Какие озера пригодны для рыбоводства?"
6. Gets list of fish-bearing water bodies

**Limitation:** Cannot prioritize inspection schedule without expert access

---

## Role Enhancement Roadmap

### Phase 1: Current Implementation ✅

- Two roles: guest and expert
- Field-level access control
- Endpoint-level protection

### Phase 2: Planned Features

- Admin role for user management
- Role approval workflow
- Audit logging for expert actions
- Time-limited expert sessions

### Phase 3: Future Enhancements

- Organization-based roles (Ministry A, Ministry B)
- Granular permissions (view priority, edit priority, upload docs)
- Regional access control (experts limited to specific regions)
- Multi-factor authentication for experts

---

## FAQ

### Q: Can a guest upgrade to expert?

**A:** Not automatically. Currently, role assignment is manual via database update. Future versions may include approval workflows.

---

### Q: What happens if JWT token expires?

**A:** User must re-authenticate. Token expiration is set to 24 hours by default (`ACCESS_TOKEN_EXPIRE_MINUTES=1440`).

---

### Q: Can experts see all water objects?

**A:** Yes, experts have full access to all objects and all fields, including priorities.

---

### Q: Why can guests see technical condition but not priority?

**A:** Technical condition is a direct assessment (1-5 scale) that's less sensitive. Priority combines multiple factors and reveals inspection planning strategy, which is operationally sensitive.

---

### Q: How are roles verified on the frontend?

**A:** Frontend receives role in login response and stores it. UI shows/hides features based on role. However, **backend always enforces** role permissions regardless of frontend state.

---

### Q: Can I have more than two roles?

**A:** Current implementation supports exactly two roles. Adding more roles requires:

1. Update `UserRole` enum in `models/user.py`
2. Update role checking logic in route dependencies
3. Update frontend role handling
4. Create migration for new role values

---

## Contact

For role-related issues or access requests:

- System Administrator: admin@gidroatlas.kz
- Technical Support: support@gidroatlas.kz

---

_Last updated: 2024_
