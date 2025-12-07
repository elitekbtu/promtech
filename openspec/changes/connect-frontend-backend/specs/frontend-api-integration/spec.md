## ADDED Requirements

### Requirement: Environment-Aware Backend Configuration

The frontend application SHALL dynamically resolve the backend API URL based on the runtime environment to support local development and production deployments.

#### Scenario: Local development default

- **WHEN** frontend runs locally without environment variables set
- **THEN** backend URL resolves to `http://localhost:8000`

#### Scenario: Custom backend URL

- **WHEN** developer sets `EXPO_PUBLIC_BACKEND_URL` in `.env` file
- **THEN** backend URL uses the custom value
- **AND** overrides all other defaults

#### Scenario: Configuration validation

- **WHEN** application starts
- **THEN** backend URL is logged to console
- **AND** configuration source is indicated (env var, default, etc.)

---

### Requirement: Water Objects API Integration

The frontend SHALL provide a type-safe service layer for accessing water object data from the backend API.

#### Scenario: List water objects with filters

- **WHEN** user requests water objects list with filters
- **THEN** frontend calls `GET /api/objects` with query parameters
- **AND** filters include region, resource_type, water_type, fauna, technical_condition, priority
- **AND** response is typed as `WaterObjectList` interface
- **AND** data includes pagination (page, page_size, total)

#### Scenario: Get single water object details

- **WHEN** user selects a water object by ID
- **THEN** frontend calls `GET /api/objects/{id}`
- **AND** response is typed as `WaterObject` interface
- **AND** response includes all fields (name, region, coordinates, priority, etc.)

#### Scenario: Guest user sees limited data

- **WHEN** user has role='guest'
- **THEN** API responses exclude `priority` and `priority_level` fields
- **AND** frontend handles missing fields gracefully

#### Scenario: Expert user sees full data

- **WHEN** user has role='expert'
- **THEN** API responses include all fields including `priority` and `priority_level`
- **AND** frontend displays priority information

---

### Requirement: Priorities API Integration

The frontend SHALL provide expert-only access to priority management features through the backend API.

#### Scenario: Fetch priority table (expert only)

- **WHEN** expert user requests priority table
- **THEN** frontend calls `GET /api/priorities/table` with auth token
- **AND** response includes water objects sorted by priority score
- **AND** each item includes technical_condition, passport_date, priority, priority_level

#### Scenario: Fetch priority statistics (expert only)

- **WHEN** expert user requests priority statistics
- **THEN** frontend calls `GET /api/priorities/stats` with auth token
- **AND** response includes counts for high/medium/low priority levels
- **AND** data is typed as `PriorityStatistics` interface

#### Scenario: Guest user blocked from priorities

- **WHEN** guest user attempts to access priority endpoints
- **THEN** frontend prevents the API call
- **OR** backend returns 403 Forbidden
- **AND** frontend displays appropriate message in Russian

---

### Requirement: RAG System API Integration

The frontend SHALL integrate with the agentic RAG system for intelligent natural language queries about water resources.

#### Scenario: Send natural language query

- **WHEN** user submits a query in Russian
- **THEN** frontend calls `POST /api/rag/query` with query text
- **AND** request includes language preference (default 'ru')
- **AND** response includes answer text and related water objects
- **AND** response is typed as `RAGResponse` interface

#### Scenario: Request priority explanation

- **WHEN** expert user requests priority explanation for an object
- **THEN** frontend calls `POST /api/rag/explain-priority/{object_id}`
- **AND** response includes AI-generated explanation in Russian
- **AND** explanation references technical condition and passport age

#### Scenario: Handle RAG system errors

- **WHEN** RAG system is unavailable or returns error
- **THEN** frontend displays user-friendly error message
- **AND** logs technical error details for debugging
- **AND** allows user to retry the query

---

### Requirement: Face ID Verification API Integration

The frontend SHALL integrate with the Face ID verification system for biometric authentication.

#### Scenario: Send face photo for verification

- **WHEN** user captures face photo during login/registration
- **THEN** frontend converts photo to base64 or FormData
- **AND** calls `POST /api/faceid/verify` with photo data
- **AND** request includes proper content-type header (multipart/form-data or application/json)

#### Scenario: Handle successful verification

- **WHEN** backend returns verified=true with confidence score
- **THEN** frontend saves JWT token and user data securely
- **AND** redirects user to main application
- **AND** displays confidence score if available

#### Scenario: Handle failed verification

- **WHEN** backend returns verified=false or error
- **THEN** frontend displays error message in Russian
- **AND** allows user to retry face capture
- **AND** suggests alternative authentication methods

---

### Requirement: Authentication Flow Integration

The frontend SHALL seamlessly integrate with the backend authentication system using JWT tokens.

#### Scenario: User registration

- **WHEN** user submits registration form with name, email, password, face photo
- **THEN** frontend calls `POST /api/auth/register`
- **AND** request includes all required fields
- **AND** successful response includes access_token and user data
- **AND** token is saved securely using SecureStore

#### Scenario: User login

- **WHEN** user submits login form with email and password
- **THEN** frontend calls `POST /api/auth/login`
- **AND** successful response includes access_token, user data, and role
- **AND** token is saved securely
- **AND** role determines UI access (guest vs expert)

#### Scenario: Authenticated API requests

- **WHEN** making API requests requiring authentication
- **THEN** frontend includes Authorization header with Bearer token
- **AND** token is retrieved from SecureStore
- **AND** requests fail gracefully if token is missing or expired

#### Scenario: Token expiration handling

- **WHEN** backend returns 401 Unauthorized due to expired token
- **THEN** frontend clears stored token and user data
- **AND** redirects user to login screen
- **AND** displays session expired message

---

### Requirement: TypeScript Type Definitions

The frontend SHALL define TypeScript interfaces matching backend Pydantic schemas for compile-time type safety.

#### Scenario: Water object types

- **WHEN** working with water object data
- **THEN** TypeScript interfaces include all backend fields
- **AND** enum values match backend exactly (in Russian)
- **AND** optional fields are marked with `?` operator

#### Scenario: Enum type definitions

- **WHEN** defining enum types (ResourceType, WaterType, FaunaType, PriorityLevel)
- **THEN** values match backend string literals exactly
- **AND** use Russian text as specified in backend models
- **AND** TypeScript enforces valid enum values

#### Scenario: API response types

- **WHEN** defining API response types
- **THEN** include both data payload and metadata (pagination, counts)
- **AND** match backend response structure exactly
- **AND** support both guest and expert response variations

---

### Requirement: Error Handling and User Feedback

The frontend SHALL provide clear, localized error messages for all API failures.

#### Scenario: Network error

- **WHEN** API request fails due to network issue
- **THEN** frontend displays "Не удалось подключиться к серверу" message
- **AND** logs technical error to console
- **AND** provides retry option

#### Scenario: Backend error (4xx, 5xx)

- **WHEN** backend returns HTTP error status
- **THEN** frontend extracts error message from response body
- **AND** displays message in Russian
- **AND** logs full error details for debugging

#### Scenario: CORS error

- **WHEN** browser blocks request due to CORS policy
- **THEN** frontend logs detailed CORS error
- **AND** displays generic connection error to user
- **AND** provides troubleshooting hint in development mode

---

### Requirement: CORS Configuration

The backend SHALL allow requests from frontend origins in all deployment environments.

#### Scenario: Local development CORS

- **WHEN** frontend runs on `localhost:19006`
- **THEN** backend CORS allows origin `http://localhost:19006`
- **AND** allows credentials
- **AND** allows all methods (GET, POST, PUT, DELETE)

#### Scenario: Production CORS

- **WHEN** deployed to production
- **THEN** backend CORS restricts to specific frontend domain
- **AND** removes wildcard `*` origin
- **AND** uses environment variable for allowed origins

---

### Requirement: Development Documentation

The project SHALL provide comprehensive documentation for connecting frontend to backend.

#### Scenario: Quick start guide

- **WHEN** new developer reads frontend README
- **THEN** instructions explain backend connection setup
- **AND** environment variables are documented
- **AND** local development workflow is covered

#### Scenario: Troubleshooting guide

- **WHEN** developer encounters connection issues
- **THEN** documentation includes common problems and solutions
- **AND** covers CORS errors, network issues, environment variables
- **AND** provides debugging commands (curl, network inspector, etc.)

#### Scenario: API documentation

- **WHEN** developer needs to use API endpoints
- **THEN** documentation lists all available endpoints
- **AND** includes request/response examples
- **AND** specifies required authentication
- **AND** references TypeScript interfaces
