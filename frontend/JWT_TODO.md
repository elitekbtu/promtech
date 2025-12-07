# JWT Authentication TODO

## Status: NOT IMPLEMENTED (Backend Ready, Waiting for Frontend)

The backend has JWT authentication code prepared but commented out to maintain backward compatibility.

## Current Behavior

- `/api/auth/register` returns `UserRead` object with role field
- `/api/auth/login` returns `UserRead` object with role field
- No JWT tokens are generated
- Role field is included in user data for client-side logic

## What Needs to Be Done (Frontend)

### 1. Update Login/Register Response Handling

Currently expecting:

```typescript
{
  id: number;
  name: string;
  email: string;
  role: "guest" | "expert"; // ✅ Already included
  // ... other fields
}
```

Future JWT response will be:

```typescript
{
  access_token: string;
  token_type: "bearer";
  user: {
    id: number;
    name: string;
    email: string;
    role: "guest" | "expert";
    // ... other fields
  }
}
```

### 2. Token Storage

Add token storage in login/register handlers:

```typescript
// After successful login/register
const response = await api.post("/auth/login", credentials);
const { access_token, user } = response.data;

// Store token
localStorage.setItem("access_token", access_token);
// Or use secure httpOnly cookies

// Store user data
setUser(user);
```

### 3. API Request Interceptor

Add Authorization header to all API requests:

```typescript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 4. Handle Token Expiration

```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem("access_token");
      // Redirect to login
    }
    return Promise.reject(error);
  }
);
```

### 5. Update Protected Route Logic

Current (role-based):

```typescript
if (user?.role === "expert") {
  // Show expert features
}
```

Future (same, but with JWT verification on backend):

```typescript
// Same client-side logic, but backend will verify JWT token
if (user?.role === "expert") {
  // Show expert features
}
```

## Backend Changes Needed (When Frontend Ready)

1. Uncomment JWT code in `backend/services/auth/service.py`
2. Uncomment JWT imports and dependencies
3. Update `create_user()` and `login_user()` to return `Token` instead of `UserRead`
4. Update router response models from `UserRead` to `Token`
5. Test JWT token generation and validation

## Files to Check

### Backend (TODO comments added):

- `backend/services/auth/service.py` - JWT functions commented out
- `backend/services/auth/router.py` - Response models use UserRead
- `backend/services/auth/schemas.py` - Token and TokenData schemas ready

### Frontend (TODO - add JWT support):

- Login component - Update response handling
- Register component - Update response handling
- API client - Add Authorization header interceptor
- Auth context/store - Add token storage and management

## Testing Checklist

When implementing:

- [ ] Frontend stores and sends JWT tokens
- [ ] Backend uncomments JWT code
- [ ] Login returns Token object
- [ ] Register returns Token object
- [ ] API requests include Authorization header
- [ ] Protected endpoints validate JWT
- [ ] Token expiration handled (7 days default)
- [ ] 401 errors trigger re-authentication
- [ ] Role-based access still works
- [ ] Guest users can't access expert endpoints (403)

## Current Priority

**LOW** - System works without JWT using existing session-based auth. Implement JWT when:

1. Frontend team is ready to handle token-based auth
2. Need for stateless authentication (scaling, mobile app, etc.)
3. Want to add token expiration/refresh logic
