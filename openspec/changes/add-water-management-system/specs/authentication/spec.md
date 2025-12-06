# Authentication Specification

## MODIFIED Requirements

### Requirement: User Role System

The system SHALL support two distinct user roles: `guest` (public read-only access) and `expert` (full access including priority data and analysis).

**Previous**: System supported `admin` and `user` roles.  
**Change**: Replace with water management domain-specific roles.

#### Scenario: Register guest user

- **GIVEN** a new user registration
- **WHEN** no role is specified
- **THEN** user SHALL be created with role="guest"

#### Scenario: Register expert user

- **GIVEN** an administrator creating a user account
- **WHEN** role="expert" is specified
- **THEN** user SHALL be created with expert privileges

#### Scenario: Login returns role-based token

- **GIVEN** a user with role="expert"
- **WHEN** logging in with valid credentials
- **THEN** JWT token SHALL include role="expert" claim

#### Scenario: Guest cannot access expert endpoints

- **GIVEN** a user with role="guest"
- **WHEN** attempting to access /priorities/table
- **THEN** 403 Forbidden SHALL be returned

#### Scenario: Expert can access all endpoints

- **GIVEN** a user with role="expert"
- **WHEN** accessing any water management endpoint
- **THEN** request SHALL be authorized

#### Scenario: Unauthenticated access defaults to guest

- **GIVEN** a request without authentication token
- **WHEN** accessing public water object endpoints
- **THEN** guest-level data visibility SHALL apply

## ADDED Requirements

### Requirement: Role-Based JWT Claims

The system SHALL include user role in JWT tokens for authorization decisions.

#### Scenario: JWT contains role claim

- **GIVEN** a successful login
- **WHEN** JWT token is generated
- **THEN** token payload SHALL include "role" field with value "guest" or "expert"

#### Scenario: Validate role claim on protected endpoints

- **GIVEN** a request to a protected endpoint
- **WHEN** JWT is validated
- **THEN** user role SHALL be extracted from token and used for authorization

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

- **GIVEN** the /ai/objects/{id}/explain-priority endpoint
- **WHEN** any request is received
- **THEN** only users with role="expert" SHALL be authorized
