# Authentication Specification

## MODIFIED Requirements

### Requirement: User Role System

The system SHALL support two distinct user roles: `guest` (public read-only access) and `expert` (full access including priority data and analysis).

**Previous**: System supported `admin` and `user` roles.  
**Change**: Replace with water management domain-specific roles.

**Status**: ✅ **JWT Implementation ACTIVE** - Role system fully implemented with JWT token authentication. Login/register endpoints return JWT tokens with user data.

#### Scenario: Register guest user

- **GIVEN** a new user registration
- **WHEN** no role is specified
- **THEN** user SHALL be created with role="guest"
- **AND** JWT token SHALL be returned with access_token and user data

#### Scenario: Register expert user

- **GIVEN** an administrator creating a user account
- **WHEN** role="expert" is specified
- **THEN** user SHALL be created with expert privileges
- **AND** JWT token SHALL be returned with access_token and user data

#### Scenario: Login returns JWT token with user data

- **GIVEN** a user with role="expert"
- **WHEN** logging in with valid credentials
- **THEN** response SHALL include JWT token with:
  - access_token (Bearer token, 7 days expiration)
  - token_type ("bearer")
  - user data with role="expert" field

#### Scenario: Guest cannot access expert endpoints

- **GIVEN** a user with role="guest"
- **WHEN** attempting to access /priorities/table with valid JWT
- **THEN** 403 Forbidden SHALL be returned

#### Scenario: Expert can access all endpoints

- **GIVEN** a user with role="expert"
- **WHEN** accessing any water management endpoint with valid JWT
- **THEN** request SHALL be authorized

#### Scenario: Authentication uses JWT Bearer tokens

- **GIVEN** a request to protected endpoints
- **WHEN** authentication is required
- **THEN** JWT Bearer token SHALL be validated from Authorization header
- **AND** User and role SHALL be extracted from token claims

## ACTIVE Requirements

### Requirement: Role-Based JWT Claims

**Status**: ✅ Fully implemented and active.

The system SHALL include user role in JWT tokens for authorization decisions.

#### Scenario: JWT contains role claim

- **GIVEN** a successful login
- **WHEN** JWT token is generated
- **THEN** token payload SHALL include:
  - "sub": user_id (string)
  - "email": user email
  - "role": "guest" or "expert"
  - "exp": expiration timestamp (7 days from issue)

#### Scenario: Validate role claim on protected endpoints

- **GIVEN** a request to a protected endpoint
- **WHEN** JWT is validated
- **THEN** user role SHALL be extracted from token and used for authorization
- **AND** `get_current_user()` dependency SHALL return authenticated User
- **AND** `require_expert()` dependency SHALL enforce expert role

### Requirement: Role Migration

The system SHALL provide migration from legacy roles to new role system.

#### Scenario: Migrate admin to expert

- **GIVEN** an existing user with role="admin"
- **WHEN** running role migration script
- **THEN** user role SHALL be updated to "expert"

#### Scenario: Migrate user to guest

- **GIVEN** an existing user with role="user"
- **WHEN** running role migration script
- **THEN** user role SHALL be updated to "guest"

### Requirement: Expert-Only Endpoint Protection

The system SHALL enforce expert role requirement on sensitive endpoints.

#### Scenario: Protect priority dashboard

- **GIVEN** the /priorities/table endpoint
- **WHEN** any request is received
- **THEN** only users with role="expert" SHALL be authorized

#### Scenario: Protect AI priority explanation

- **GIVEN** the /api/rag/explain-priority/{object_id} endpoint
- **WHEN** any request is received
- **THEN** only users with role="expert" SHALL be authorized
