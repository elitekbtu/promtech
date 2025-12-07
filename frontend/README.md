# Frontend - GidroAtlas

React Native Expo application for water infrastructure monitoring with AI-powered RAG system.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

### Environment Configuration

Create a `.env` file in the frontend directory:

```bash
# Backend API URL (defaults to localhost:8000 if not set)
EXPO_PUBLIC_BACKEND_URL=http://localhost:8000

# Gemini API Key (for RAG features)
EXPO_PUBLIC_GEMINI_API_KEY=your-gemini-api-key-here
```

**Note**: The app defaults to `http://localhost:8000` for local development. Set `EXPO_PUBLIC_BACKEND_URL` to connect to a different backend server.

## 📱 Features

### 1. Water Infrastructure Monitoring

- **Browse water objects**: List, filter, and sort hydro-technical structures
- **Priority system**: Expert-only view of risk priorities
- **Passport documents**: Upload and view infrastructure passports
- **Role-based access**: Guest (read-only) and Expert (full access)

### 2. AI-Powered RAG System

- **Natural language queries**: Ask questions about water infrastructure
- **Priority explanations**: Get AI explanations for priority scores (expert only)
- **Vector search**: Find relevant documents and data
- **Multi-language**: Russian primary, English supported

### 3. Authentication

- **JWT-based authentication**: Secure token storage with expo-secure-store
- **Face ID verification**: Biometric authentication
- **Role management**: Guest and Expert user roles

## 🔧 Configuration

### Backend Integration

The app uses a type-safe API service layer (`lib/api-services.ts`) that connects to the FastAPI backend:

- **Configuration**: Backend URL is resolved via `lib/config.ts` (uses `EXPO_PUBLIC_BACKEND_URL` or defaults to localhost:8000)
- **Authentication**: JWT tokens stored securely with expo-secure-store
- **Type Safety**: All API types defined in `lib/gidroatlas-types.ts` matching backend Pydantic schemas

### API Services

Import and use the unified API:

```typescript
import gidroatlasAPI from "@/lib/api-services";

// List water objects
const objects = await gidroatlasAPI.waterObjects.list({
  water_type: "Река",
  limit: 20,
});

// Login
const { access_token, user } = await gidroatlasAPI.auth.login({
  email: "user@example.com",
  password: "password123",
});

// Query RAG system
const response = await gidroatlasAPI.rag.query({
  query: "Какие объекты требуют срочного ремонта?",
  language: "ru",
});
```

### Backend URL

The backend URL is configured in multiple places (in priority order):

1. **Environment variable** (`.env` file):

   ```bash
   EXPO_PUBLIC_BACKEND_URL=http://46.101.175.118:8000
   ```

2. **App config** (`app.json`):

   ```json
   {
     "expo": {
       "extra": {
         "BACKEND_URL": "http://46.101.175.118:8000"
       }
     }
   }
   ```

3. **Default fallback**: `http://46.101.175.118:8000`

### Gemini API Key

Set your Gemini API key in `app.json`:

```json
{
  "expo": {
    "extra": {
      "GEMINI_API_KEY": "your-key-here"
    }
  }
}
```

## 🧠 RAG Integration

The Live Chat is integrated with the backend RAG system:

### How it works

1. User speaks or types a question
2. Gemini analyzes and decides which tools to call
3. Frontend intercepts tool calls and routes to backend
4. Backend executes tools (vector_search or web_search)
5. Results returned to Gemini
6. Gemini synthesizes answer with sources

### Tool Selection

- **vector_search**: Company policies, internal documents
- **web_search**: Current events, public information

### RAG Health Indicator

Look for the **🧠 RAG** indicator in the Live Chat header:

- **Green**: RAG tools are healthy and ready
- **Red**: RAG tools have issues (check backend)

## 📂 Project Structure

```
frontend/
├── app/                    # Screens (Expo Router)
│   ├── (tabs)/
│   │   ├── index.tsx      # Home
│   │   ├── explore.tsx    # Products
│   │   ├── live-chat.tsx  # Gemini Live + RAG
│   │   └── face-verify.tsx
│   └── _layout.tsx
├── components/            # Reusable components
├── hooks/                # Custom hooks
│   ├── use-live-api-with-rag.ts
│   └── use-rag-tools.ts
├── lib/                  # Libraries and utilities
│   ├── config.ts         # Configuration management
│   ├── rag-tools-client.ts
│   └── genai-live-client.ts
├── contexts/             # React contexts
└── constants/            # App constants
```

## 🎯 Available Scripts

```bash
# Start development server
npm start

# Start on specific platform
npm run ios
npm run android
npm run web

# Lint code
npm run lint

# Reset project (clean cache)
npm run reset-project
```

## 🐛 Debugging

### Check Backend Connection

```bash
# Check if backend is reachable
curl http://46.101.175.118:8000/api/health

# Check RAG tools status
curl http://46.101.175.118:8000/api/rag/live/health
```

### Console Logs

Look for these logs in the browser/expo console:

```
[Config] Backend URL: http://46.101.175.118:8000
[RAG Tools Client] Initialized with URL: http://46.101.175.118:8000
[RAG Tools] Loading function declarations...
[RAG Tools] Loaded tools: vector_search, web_search
[RAG Tools] Health status: { status: 'healthy' }
```

### Common Issues

**RAG tools not loading:**

- Check backend is running
- Verify backend URL in config
- Check network connectivity

**Gemini not calling tools:**

- Verify tools are registered (check logs)
- Ensure Gemini API key is valid
- Check system prompts include tool instructions

**Face verification not working:**

- Check camera permissions
- Verify backend faceid endpoint is accessible
- Check API URL configuration

## 🌐 Environment Modes

### Development (Local)

```bash
EXPO_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Production (Server)

```bash
EXPO_PUBLIC_BACKEND_URL=http://46.101.175.118:8000
```

Default is production mode.

## 📝 Notes

- The app uses Expo Router for navigation
- Configuration is centralized in `lib/config.ts`
- RAG tools are automatically loaded when Live Chat connects
- Face verification requires camera permissions

## 🔗 Related Documentation

- [Gemini Live + RAG Integration](../docs/gemini-live-rag-integration.md)
- [Backend API Docs](http://46.101.175.118:8000/docs)
- [Expo Documentation](https://docs.expo.dev)

## 📄 License

MIT
