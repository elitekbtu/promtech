# Frontend JWT Authentication Refactoring

## ✅ Completed Changes

This document describes the frontend refactoring to support JWT authentication with the backend.

---

## 📦 New Dependencies

Added via `npm install expo-secure-store axios`:

- **expo-secure-store**: Secure storage for JWT tokens (uses Keychain on iOS, KeyStore on Android)
- **axios**: HTTP client with interceptor support for automatic JWT injection

---

## 📁 New Files Created

### 1. `lib/auth.ts` - Authentication Utility Module

**Purpose**: Secure storage and retrieval of JWT tokens and user data

**Key Functions**:

```typescript
- saveAuthToken(token: string): Promise<void>
- getAuthToken(): Promise<string | null>
- saveUserData(user: UserData): Promise<void>
- getUserData(): Promise<UserData | null>
- saveAuthResponse(tokenResponse: TokenResponse): Promise<void>
- isAuthenticated(): Promise<boolean>
- isExpertUser(): Promise<boolean>
- getUserRole(): Promise<'guest' | 'expert' | null>
- clearAuth(): Promise<void>
```

**Usage Example**:

```typescript
import { saveAuthResponse, getUserData } from "@/lib/auth";

// After login
await saveAuthResponse(tokenResponse);

// Check user role
const user = await getUserData();
console.log(user.role); // 'guest' or 'expert'
```

---

### 2. `lib/axios-client.ts` - HTTP Client with JWT Interceptors

**Purpose**: Axios instance configured for automatic JWT token injection and 401 handling

**Features**:

- ✅ Automatically adds `Authorization: Bearer <token>` to all requests
- ✅ Handles 401 errors (expired tokens) → clears auth and redirects to login
- ✅ Handles 403 errors (insufficient permissions)
- ✅ Development logging for debugging

**Usage Example**:

```typescript
import apiClient from "@/lib/axios-client";

// Token automatically included in headers
const response = await apiClient.get("/api/objects");
```

**Request Interceptor**:

```typescript
// Automatically adds JWT token from SecureStore
config.headers.Authorization = `Bearer ${token}`;
```

**Response Interceptor**:

```typescript
// Handles 401 (token expired)
if (status === 401) {
  await clearAuth();
  router.replace("/login");
}
```

---

### 3. `lib/api-services.ts` - API Service Layer

**Purpose**: Typed API functions for all backend endpoints

**Services**:

- `WaterObjectsAPI`: CRUD operations for water objects
- `PrioritiesAPI`: Expert-only priority endpoints
- `PassportsAPI`: Passport PDF upload/retrieval

**Usage Example**:

```typescript
import { WaterObjectsAPI, PrioritiesAPI } from "@/lib/api-services";

// Get water objects (guest or expert)
const objects = await WaterObjectsAPI.getList({
  region: "Almaty",
  limit: 20,
});

// Get priorities (expert only - will 403 if guest)
const stats = await PrioritiesAPI.getStatistics();
```

---

### 4. `hooks/use-auth.ts` - Authentication React Hooks

**Purpose**: React hooks for role-based UI and auth state management

**Hooks**:

#### `useUser()`

```typescript
const { user, loading, error, refresh } = useUser();
// Returns current user data with role
```

#### `useAuth()`

```typescript
const { authenticated, loading } = useAuth();
// Returns authentication status
```

#### `useUserRole()`

```typescript
const { role, isGuest, isExpert, loading } = useUserRole();
// Returns user role and helpers
```

#### `useIsExpert()`

```typescript
const { isExpert, loading } = useIsExpert();
// Returns true if user is expert
```

#### `useRequireRole(role)`

```typescript
const canEdit = useRequireRole("expert");
// Returns true if user has required role
```

#### `useAuthState()`

```typescript
const { user, authenticated, loading, isExpert } = useAuthState();
// All-in-one auth state hook
```

**Usage Example**:

```typescript
import { useUserRole } from "@/hooks/use-auth";

function MyComponent() {
  const { isExpert, loading } = useUserRole();

  if (loading) return <ActivityIndicator />;

  return <>{isExpert && <Button title="Upload Passport" />}</>;
}
```

---

## 🔄 Modified Files

### `app/login.tsx`

**Changes**:

1. ✅ Updated imports to use new auth utilities
2. ✅ Updated `UserData` type to include `role` field
3. ✅ Updated `FaceVerificationResult` to expect `TokenResponse`
4. ✅ Replaced `saveUserSession()` to use `saveAuthResponse()`
5. ✅ Updated login handler to extract `TokenResponse`
6. ✅ Updated register handler to extract `TokenResponse`

**Key Changes**:

```typescript
// OLD: Expecting UserData
const userData: UserData = await loginResponse.json();
await saveUserSession(userData);

// NEW: Expecting TokenResponse
const tokenData: TokenResponse = await loginResponse.json();
await saveAuthResponse(tokenData);
console.log("Role:", tokenData.user.role);
```

---

## 🎯 How It Works

### Authentication Flow

1. **Login/Register**:

   ```
   User credentials → Backend → TokenResponse {
     access_token: "eyJ...",
     token_type: "bearer",
     user: { id, name, role, ... }
   }
   ```

2. **Store Token**:

   ```
   TokenResponse → saveAuthResponse() → SecureStore
   - access_token saved to 'jwt_access_token'
   - user data saved to 'user_data'
   ```

3. **API Requests**:

   ```
   apiClient.get('/api/objects')
   → Request Interceptor adds: Authorization: Bearer <token>
   → Backend validates JWT
   → Returns role-based response
   ```

4. **Token Expiration**:
   ```
   Backend returns 401
   → Response Interceptor catches
   → clearAuth() removes token
   → router.replace('/login')
   ```

---

## 🚀 Usage Examples

### Making Authenticated Requests

```typescript
import apiClient from "@/lib/axios-client";
import { WaterObjectsAPI } from "@/lib/api-services";

// Option 1: Use service layer (recommended)
const objects = await WaterObjectsAPI.getList();

// Option 2: Direct axios call
const response = await apiClient.get("/api/objects");
```

### Role-Based UI

```typescript
import { useUserRole } from "@/hooks/use-auth";

function Dashboard() {
  const { isExpert, loading } = useUserRole();

  return (
    <View>
      <Text>Water Objects</Text>

      {/* Expert-only features */}
      {isExpert && (
        <>
          <Button title="Create Object" onPress={createObject} />
          <Button title="View Priorities" onPress={viewPriorities} />
        </>
      )}
    </View>
  );
}
```

### Checking Authentication

```typescript
import { isAuthenticated, clearAuth } from "@/lib/auth";
import { router } from "expo-router";

async function handleLogout() {
  await clearAuth();
  router.replace("/login");
}

async function checkAuth() {
  if (!(await isAuthenticated())) {
    router.replace("/login");
  }
}
```

---

## 🔒 Security Notes

1. **Secure Storage**:

   - iOS: Uses Keychain
   - Android: Uses KeyStore with AES encryption
   - Web: Falls back to localStorage (less secure)

2. **Token Expiration**:

   - Backend sets 7-day expiration
   - Automatically handled by axios interceptor

3. **HTTPS Required**:
   - Always use HTTPS in production
   - Tokens transmitted in Authorization header

---

## ⚠️ Backend Update Required

The Face ID verification endpoint needs to be updated to return `TokenResponse` instead of user data:

```python
# Current (incorrect)
return {"success": True, "verified": True, "user": {...}}

# Required (correct)
token = create_access_token(user.id, user.email, user.role)
return {
    "success": True,
    "verified": True,
    "token": {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user)
    }
}
```

---

## 🧪 Testing Checklist

- [ ] Login with email/password returns JWT token
- [ ] Register with Face ID returns JWT token
- [ ] Face ID login returns JWT token
- [ ] JWT token stored in SecureStore
- [ ] Subsequent API calls include Authorization header
- [ ] Guest users see limited data
- [ ] Expert users see full data with priorities
- [ ] Expert-only endpoints return 403 for guests
- [ ] Expired tokens trigger logout and redirect
- [ ] Logout clears all auth data

---

## 📚 Additional Resources

- [Expo SecureStore Docs](https://docs.expo.dev/versions/latest/sdk/securestore/)
- [Axios Interceptors](https://axios-http.com/docs/interceptors)
- [JWT Best Practices](https://jwt.io/introduction)
