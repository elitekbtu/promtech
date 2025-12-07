# RAG Endpoint Enhancements Specification

## MODIFIED Requirements

### Requirement: Water Management Query Processing

The EXISTING `/api/rag/query` endpoint SHALL be enhanced to handle water management domain queries with context-aware processing.

#### Scenario: Query about regional objects

- **GIVEN** a user query "Какие водоемы с высоким приоритетом в Улытауском регионе?"
- **WHEN** POST /api/rag/query with query and language="ru"
- **THEN** response SHALL include: natural language answer, list of matching water objects with IDs and priorities, source citations

#### Scenario: Follow-up question with context

- **GIVEN** previous conversation about specific region (conversation_id in request)
- **WHEN** user asks "А сколько из них озера?"
- **THEN** RAG system SHALL understand context and filter previous results by resource_type="lake"

#### Scenario: Handle ambiguous queries

- **GIVEN** a vague query without clear filters
- **WHEN** RAG system processes query
- **THEN** response SHALL either ask clarifying questions or provide general information with caveats

## ADDED Requirements

### Requirement: Priority Explanation Convenience Endpoint

The system SHALL provide a convenience wrapper `POST /api/rag/explain-priority/{object_id}` that prepares context and calls RAG query.

#### Scenario: Explain high priority object

- **GIVEN** a water object with high priority (score 14)
- **WHEN** POST /api/rag/explain-priority/5 with language="ru"
- **THEN** endpoint SHALL: fetch object data, fetch passport content, construct RAG query with context, return explanation with technical_condition justification, passport age analysis, priority formula breakdown

#### Scenario: Include passport context in explanation

- **GIVEN** a water object with passport containing degradation details
- **WHEN** requesting priority explanation
- **THEN** endpoint SHALL inject passport excerpts into RAG query context
- **AND** explanation SHALL reference specific passport findings (e.g., "высокая степень зарастания")

#### Scenario: Expert-only access

- **GIVEN** a user with role="guest"
- **WHEN** attempting to access /api/rag/explain-priority/{object_id}
- **THEN** 403 Forbidden SHALL be returned

## MODIFIED Requirements

### Requirement: Enhanced Query Request Schema

The EXISTING `QueryRequest` schema SHALL be extended to support water domain context.

#### Scenario: Filter by object context

- **GIVEN** a QueryRequest with object_id=5
- **WHEN** processing query
- **THEN** RAG system SHALL inject water object details into context

#### Scenario: Filter by region or priority

- **GIVEN** a QueryRequest with filters={"region": "Ulytau", "min_priority": 10}
- **WHEN** water_search tool is invoked
- **THEN** SQL query SHALL apply these filters

### Requirement: Enhanced Query Response Schema

The EXISTING `QueryResponse` schema SHALL include water-specific source attribution.

#### Scenario: Cite water objects

- **GIVEN** a response mentioning specific water bodies
- **WHEN** formatting QueryResponse
- **THEN** sources list SHALL include object IDs, names, and types

#### Scenario: Cite passport documents

- **GIVEN** a response using passport data
- **WHEN** formatting QueryResponse
- **THEN** sources list SHALL include passport document references with page/section numbers

### Requirement: Domain-Specific Response Formatting

The system SHALL format AI responses with water management terminology and structure.

#### Scenario: Use technical terms correctly

- **GIVEN** a response about water bodies
- **WHEN** generating text
- **THEN** terminology SHALL match domain standards (озеро/водохранилище/канал, пресная/непресная вода, etc.)

#### Scenario: Structure complex responses

- **GIVEN** a query returning multiple objects
- **WHEN** formatting QueryResponse
- **THEN** information SHALL be organized by region, priority, or other logical grouping

#### Scenario: Include quantitative data

- **GIVEN** information about water objects
- **WHEN** generating response
- **THEN** relevant numbers SHALL be included (priority scores, counts, coordinates)

### Requirement: Error Handling for RAG Queries

The RAG system SHALL gracefully handle errors and edge cases.

#### Scenario: Handle non-existent object ID in explain-priority

- **GIVEN** a request to /api/rag/explain-priority/9999
- **WHEN** object 9999 does not exist
- **THEN** 404 Not Found SHALL be returned with helpful message

#### Scenario: Handle Gemini API failure

- **GIVEN** Gemini API is unavailable
- **WHEN** processing RAG query
- **THEN** 503 Service Unavailable SHALL be returned with retry guidance

#### Scenario: Handle timeout on complex queries

- **GIVEN** a query requiring extensive tool invocations
- **WHEN** max agent iterations reached
- **THEN** partial response SHALL be returned with indication of incomplete analysis

### Requirement: Query Language Support

The RAG system SHALL support queries in Russian with Russian responses.

#### Scenario: Process Russian input

- **GIVEN** a query in Russian
- **WHEN** analyzing intent and extracting entities
- **THEN** system prompts and tool descriptions SHALL guide agent to parse Russian correctly

#### Scenario: Generate Russian output

- **GIVEN** query results
- **WHEN** generating final response
- **THEN** output SHALL be grammatically correct Russian with proper technical terminology

### Requirement: Response Caching for Common Queries

The RAG system SHALL cache responses for frequently asked questions to reduce API costs.

#### Scenario: Cache regional summaries

- **GIVEN** a query about all objects in a region
- **WHEN** same query is made within 1 hour
- **THEN** cached response SHALL be returned without LLM call

#### Scenario: Invalidate cache on data changes

- **GIVEN** cached responses exist
- **WHEN** water object data is updated
- **THEN** relevant cached responses SHALL be invalidated
