# Water Objects Management Specification

## ADDED Requirements

### Requirement: Water Object Data Model

The system SHALL store comprehensive information about water bodies including geographic, technical, and administrative data.

#### Scenario: Store lake with complete metadata

- **GIVEN** a water body exists in Kazakhstan
- **WHEN** creating a water object record
- **THEN** the system SHALL store: id, name, region, resource_type (lake/canal/reservoir), water_type (fresh/non_fresh), fauna (boolean), passport_date, technical_condition (1-5), latitude, longitude, pdf_url, priority, priority_level, osm_id

#### Scenario: Enforce technical condition range

- **GIVEN** a water object being created or updated
- **WHEN** technical_condition is provided
- **THEN** the value SHALL be between 1 (excellent) and 5 (critical)

#### Scenario: Store geographic coordinates

- **GIVEN** a water object with location data
- **WHEN** saving coordinates
- **THEN** latitude SHALL be stored with 8 decimal precision and longitude with 11 decimal precision for accurate mapping

### Requirement: List Water Objects with Filtering

The system SHALL provide a paginated list of water objects with comprehensive filtering options.

#### Scenario: Filter by region

- **GIVEN** multiple water objects across different regions
- **WHEN** requesting objects with region="Улытауская область"
- **THEN** only objects in that region SHALL be returned

#### Scenario: Filter by resource type

- **GIVEN** water objects of types lake, canal, and reservoir
- **WHEN** requesting objects with resource_type="lake"
- **THEN** only lake objects SHALL be returned

#### Scenario: Filter by water type

- **GIVEN** water objects with fresh and non-fresh water
- **WHEN** requesting objects with water_type="fresh"
- **THEN** only fresh water objects SHALL be returned

#### Scenario: Filter by fauna presence

- **GIVEN** water objects with and without fauna
- **WHEN** requesting objects with has_fauna=true
- **THEN** only objects with fauna SHALL be returned

#### Scenario: Filter by passport date range

- **GIVEN** water objects with various passport dates
- **WHEN** requesting objects with passport_date_from="2020-01-01" and passport_date_to="2023-12-31"
- **THEN** only objects with passport dates in that range SHALL be returned

#### Scenario: Filter by technical condition range

- **GIVEN** water objects with technical_condition from 1 to 5
- **WHEN** requesting objects with technical_condition_min=3 and technical_condition_max=5
- **THEN** only objects with condition 3, 4, or 5 SHALL be returned

#### Scenario: Search by name

- **GIVEN** water objects with various names
- **WHEN** requesting objects with search="Бараккол"
- **THEN** objects with names containing "Бараккол" (case-insensitive) SHALL be returned

#### Scenario: Paginate results

- **GIVEN** 150 water objects in the database
- **WHEN** requesting page=2 with page_size=20
- **THEN** objects 21-40 SHALL be returned with total count 150

### Requirement: Sort Water Objects

The system SHALL allow sorting water objects by multiple fields in ascending or descending order.

#### Scenario: Sort by name alphabetically

- **GIVEN** water objects with various names
- **WHEN** requesting sort_by="name" and sort_order="asc"
- **THEN** objects SHALL be returned in alphabetical order by name

#### Scenario: Sort by priority descending

- **GIVEN** water objects with various priority scores
- **WHEN** requesting sort_by="priority" and sort_order="desc"
- **THEN** objects SHALL be returned with highest priority first

#### Scenario: Sort by passport date

- **GIVEN** water objects with various passport dates
- **WHEN** requesting sort_by="passport_date" and sort_order="asc"
- **THEN** objects SHALL be returned with oldest passport dates first

### Requirement: Retrieve Single Water Object

The system SHALL provide detailed information about a specific water object by ID.

#### Scenario: Get object by ID

- **GIVEN** a water object with id=5 exists
- **WHEN** requesting GET /objects/5
- **THEN** all fields for that object SHALL be returned

#### Scenario: Handle non-existent object

- **GIVEN** no water object with id=999
- **WHEN** requesting GET /objects/999
- **THEN** 404 Not Found SHALL be returned

### Requirement: Role-Based Field Visibility

The system SHALL show different fields based on user role (guest vs expert).

#### Scenario: Guest view excludes sensitive fields

- **GIVEN** a user with role="guest"
- **WHEN** requesting water objects
- **THEN** response SHALL NOT include technical_condition, priority, or priority_level fields

#### Scenario: Expert view includes all fields

- **GIVEN** a user with role="expert"
- **WHEN** requesting water objects
- **THEN** response SHALL include all fields including technical_condition, priority, and priority_level

#### Scenario: Unauthenticated defaults to guest view

- **GIVEN** a request without authentication token
- **WHEN** requesting water objects
- **THEN** response SHALL use guest field visibility rules

### Requirement: Geographic Indexing

The system SHALL efficiently query water objects by geographic location.

#### Scenario: Query objects near coordinates

- **GIVEN** water objects with various coordinates
- **WHEN** querying by latitude/longitude range
- **THEN** results SHALL be returned efficiently using spatial index

### Requirement: Bulk Operations

The system SHALL support efficient bulk import of water objects for data seeding.

#### Scenario: Import from OSM data

- **GIVEN** OpenStreetMap data for Kazakhstan water bodies
- **WHEN** running import script
- **THEN** objects SHALL be created in batch with default values for technical fields
