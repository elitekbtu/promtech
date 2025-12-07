# Authentication Specification

## MODIFIED Requirements

### Requirement: User Role System

The system SHALL support two distinct user roles: `guest` (public read-only access) and `expert` (full access including priority data and analysis).

**Previous**: System supported `admin` and `user` roles.  
**Change**: Replace with water management domain-specific roles.

**Status**: ⚠️ **JWT Implementation Deferred** - Role system implemented in database and models, but JWT token authentication is commented out to maintain backward compatibility with frontend. Login/register endpoints return `UserRead` instead of JWT tokens.

#### Scenario: Register guest user

- **GIVEN** a new user registration
- **WHEN** no role is specified
- **THEN** user SHALL be created with role="guest"

#### Scenario: Register expert user

- **GIVEN** an administrator creating a user account
- **WHEN** role="expert" is specified
- **THEN** user SHALL be created with expert privileges

#### Scenario: Login returns user data with role

- **GIVEN** a user with role="expert"
- **WHEN** logging in with valid credentials
- **THEN** response SHALL include user data with role="expert" field
- **NOTE**: JWT token implementation is deferred (TODO: implement when frontend ready)

#### Scenario: Guest cannot access expert endpoints

- **GIVEN** a user with role="guest"
- **WHEN** attempting to access /priorities/table
- **THEN** 403 Forbidden SHALL be returned

#### Scenario: Expert can access all endpoints

- **GIVEN** a user with role="expert"
- **WHEN** accessing any water management endpoint
- **THEN** request SHALL be authorized

#### Scenario: Authentication uses existing session mechanism

- **GIVEN** a request to protected endpoints
- **WHEN** authentication is required
- **THEN** existing session-based auth SHALL be used (not JWT)
- **NOTE**: JWT implementation is available but commented out for future use

## DEFERRED Requirements (TODO)

### Requirement: Role-Based JWT Claims (FUTURE IMPLEMENTATION)

**Status**: 🔜 Code prepared but commented out. Requires frontend implementation.

The system WILL (future) include user role in JWT tokens for authorization decisions.

#### Scenario: JWT contains role claim (DEFERRED)

- **GIVEN** a successful login
- **WHEN** JWT token is generated (future)
- **THEN** token payload SHALL include "role" field with value "guest" or "expert"
- **NOTE**: Helper functions exist in `auth/service.py` but are commented out

#### Scenario: Validate role claim on protected endpoints (DEFERRED)

- **GIVEN** a request to a protected endpoint
- **WHEN** JWT is validated (future)
- **THEN** user role SHALL be extracted from token and used for authorization
- **NOTE**: `get_current_user()`, `require_expert()` dependencies prepared but not active

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
