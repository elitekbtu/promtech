# Frontend JWT Authentication - Quick Start Guide

## 🎯 What Was Done

The frontend has been refactored to support JWT authentication with role-based access control (guest/expert roles).

## 📦 Installation

Already completed:

```bash
npm install expo-secure-store axios
```

## 🆕 New Files

| File                                        | Purpose                               |
| ------------------------------------------- | ------------------------------------- |
| `lib/auth.ts`                               | Secure token storage with SecureStore |
| `lib/axios-client.ts`                       | HTTP client with JWT interceptors     |
| `lib/api-services.ts`                       | Typed API service layer               |
| `hooks/use-auth.ts`                         | Authentication React hooks            |
| `components/example-water-objects-list.tsx` | Example component                     |
| `AUTHENTICATION_REFACTOR.md`                | Full documentation                    |

## 🚀 Quick Start

### 1. Making API Calls

```typescript
import { WaterObjectsAPI } from "@/lib/api-services";

// Fetch water objects (token automatically included)
const objects = await WaterObjectsAPI.getList();

// Create object (expert only)
const newObject = await WaterObjectsAPI.create({
  name: "Test Reservoir",
  region: "Almaty",
  resource_type: "reservoir",
  technical_condition: 4,
});
```

### 2. Role-Based UI

```typescript
import { useUserRole } from "@/hooks/use-auth";

function MyComponent() {
  const { isExpert, loading } = useUserRole();

  return (
    <View>
      <Text>Water Objects</Text>
      {isExpert && <Button title="Create" />}
    </View>
  );
}
```

### 3. Check Authentication

```typescript
import { isAuthenticated, getUserData } from "@/lib/auth";

const authenticated = await isAuthenticated();
const user = await getUserData();
console.log(user.role); // 'guest' or 'expert'
```

### 4. Logout

```typescript
import { clearAuth } from "@/lib/auth";
import { router } from "expo-router";

async function handleLogout() {
  await clearAuth();
  router.replace("/login");
}
```

## 🔄 How Authentication Works

1. **Login** → Backend returns `{ access_token, token_type, user }`
2. **Storage** → Token saved to SecureStore (Keychain/KeyStore)
3. **API Calls** → Axios automatically adds `Authorization: Bearer <token>`
4. **Role Check** → Backend validates token and returns role-based data
5. **Expiration** → 401 error triggers auto-logout and redirect

## 🎨 Role-Based Features

### Guest Users Can:

- ✅ View water objects (limited data)
- ✅ View passport texts
- ❌ No priority information
- ❌ Cannot create/edit/delete

### Expert Users Can:

- ✅ View water objects (full data + priorities)
- ✅ Create/Update/Delete water objects
- ✅ View priority statistics and dashboard
- ✅ Upload/Delete passport PDFs
- ✅ All guest features

## 🧪 Testing

### Manual Testing Steps:

1. **Test Login**:

   - Enter email/password → Should redirect to tabs
   - Check SecureStore has token: `await getAuthToken()`

2. **Test API Call**:

   - Fetch water objects → Should include Authorization header
   - Check Network tab for `Authorization: Bearer ...`

3. **Test Role Access**:

   - Login as guest → No priority data
   - Login as expert → See priority scores

4. **Test Token Expiration**:

   - Wait 7 days (or manually delete token backend-side)
   - Make API call → Should redirect to login

5. **Test Logout**:
   - Click logout → Token cleared, redirected to login

## ⚠️ Important Notes

### Backend Update Required

Face ID verification endpoint needs updating:

```python
# In backend/faceid/router.py
# CHANGE THIS:
return {"success": True, "verified": True, "user": {...}}

# TO THIS:
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

### Environment Variables

Make sure `SECRET_KEY` is set in backend `.env`:

```
SECRET_KEY=your-super-secret-key-change-in-production
```

### HTTPS in Production

⚠️ **CRITICAL**: Use HTTPS in production to protect JWT tokens

## 📖 Available Hooks

```typescript
// Get user data
const { user, loading } = useUser();

// Check authentication
const { authenticated, loading } = useAuth();

// Get user role
const { role, isGuest, isExpert } = useUserRole();

// Check if expert
const { isExpert } = useIsExpert();

// Require specific role
const canEdit = useRequireRole("expert");

// All-in-one
const { user, authenticated, isExpert } = useAuthState();
```

## 🔧 Troubleshooting

### "401 Unauthorized" on every request

- Check if token exists: `await getAuthToken()`
- Check backend SECRET_KEY matches
- Verify token not expired (7 days)

### "403 Forbidden" on expert endpoints

- Check user role: `const user = await getUserData(); console.log(user.role)`
- Verify backend assigned expert role

### Token not persisting

- Check SecureStore availability: `await isSecureStoreAvailable()`
- On web, check localStorage in DevTools

### Interceptor not working

- Verify importing from `@/lib/axios-client`
- Check `__DEV__` logs in console

## 📚 Full Documentation

See `AUTHENTICATION_REFACTOR.md` for complete documentation including:

- Detailed architecture
- All API functions
- Security best practices
- Complete code examples

## 🎯 Next Steps

1. ✅ Update backend Face ID endpoint to return Token
2. ✅ Test login/register flow
3. ✅ Test role-based UI components
4. ✅ Test API calls with authentication
5. ✅ Test token expiration handling

## 💡 Example Component

Check `components/example-water-objects-list.tsx` for a complete working example showing:

- Authentication hooks
- API calls
- Role-based UI
- Error handling
- Refresh functionality
