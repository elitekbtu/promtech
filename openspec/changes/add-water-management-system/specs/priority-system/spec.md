# Priority System Specification

## ADDED Requirements

### Requirement: Priority Score Calculation

The system SHALL calculate inspection priority for water objects using the formula: `priority = (6 - technical_condition) * 3 + passport_age_years` where passport_age_years = current_year - year(passport_date).

#### Scenario: Calculate high priority for poor condition

- **GIVEN** a water object with technical_condition=5 and passport_date="2016-01-01"
- **WHEN** calculating priority in year 2025
- **THEN** priority SHALL be (6-5)\*3 + (2025-2016) = 3 + 9 = 12

#### Scenario: Calculate low priority for good condition

- **GIVEN** a water object with technical_condition=2 and passport_date="2023-01-01"
- **WHEN** calculating priority in year 2025
- **THEN** priority SHALL be (6-2)\*3 + (2025-2023) = 12 + 2 = 14

#### Scenario: Handle missing passport date

- **GIVEN** a water object with no passport_date
- **WHEN** calculating priority
- **THEN** passport_age_years SHALL be treated as 0

### Requirement: Priority Level Classification

The system SHALL classify priority scores into three levels: high, medium, low.

#### Scenario: Classify high priority

- **GIVEN** a water object with priority score >= 12
- **WHEN** determining priority_level
- **THEN** priority_level SHALL be "high"

#### Scenario: Classify medium priority

- **GIVEN** a water object with priority score between 6 and 11 inclusive
- **WHEN** determining priority_level
- **THEN** priority_level SHALL be "medium"

#### Scenario: Classify low priority

- **GIVEN** a water object with priority score < 6
- **WHEN** determining priority_level
- **THEN** priority_level SHALL be "low"

### Requirement: Automatic Priority Updates

The system SHALL recalculate priority when relevant fields change.

#### Scenario: Recalculate on condition update

- **GIVEN** a water object with existing priority
- **WHEN** technical_condition is updated
- **THEN** priority and priority_level SHALL be automatically recalculated

#### Scenario: Recalculate on passport date update

- **GIVEN** a water object with existing priority
- **WHEN** passport_date is updated
- **THEN** priority and priority_level SHALL be automatically recalculated

### Requirement: Priority Dashboard for Experts

The system SHALL provide an expert-only dashboard showing objects sorted by inspection priority.

#### Scenario: Access priority table as expert

- **GIVEN** a user with role="expert"
- **WHEN** requesting GET /priorities/table
- **THEN** a list of water objects sorted by priority descending SHALL be returned

#### Scenario: Block priority table for guests

- **GIVEN** a user with role="guest"
- **WHEN** requesting GET /priorities/table
- **THEN** 403 Forbidden SHALL be returned

#### Scenario: Filter priority table by region

- **GIVEN** an expert user
- **WHEN** requesting /priorities/table?region="Улытауская область"
- **THEN** only objects in that region SHALL be returned, sorted by priority

#### Scenario: Filter by priority level

- **GIVEN** an expert user
- **WHEN** requesting /priorities/table?priority_level="high"
- **THEN** only objects with high priority SHALL be returned

### Requirement: Priority Filtering

The system SHALL allow experts to filter objects by priority range.

#### Scenario: Filter by minimum priority

- **GIVEN** an expert user
- **WHEN** requesting objects with priority_min=10
- **THEN** only objects with priority >= 10 SHALL be returned

#### Scenario: Filter by priority range

- **GIVEN** an expert user
- **WHEN** requesting objects with priority_min=8 and priority_max=12
- **THEN** only objects with priority between 8 and 12 inclusive SHALL be returned

### Requirement: Priority Explanation

The system SHALL provide human-readable explanations of priority calculations.

#### Scenario: Explain high priority

- **GIVEN** a water object with technical_condition=5, passport_date="2015-01-01"
- **WHEN** requesting priority explanation
- **THEN** the system SHALL return: current condition score, passport age in years, total priority, and classification reasoning

### Requirement: Bulk Priority Recalculation

The system SHALL support recalculating priorities for all objects (e.g., annual update).

#### Scenario: Recalculate all priorities on year change

- **GIVEN** the calendar year has changed
- **WHEN** running priority recalculation script
- **THEN** all water objects SHALL have updated priority scores reflecting new passport ages
