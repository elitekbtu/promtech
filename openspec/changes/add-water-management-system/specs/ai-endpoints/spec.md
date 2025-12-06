# AI Endpoints Specification

## ADDED Requirements

### Requirement: Water Management Chat Endpoint

The system SHALL provide a chat endpoint for natural language queries about water objects and regions.

#### Scenario: Query about regional objects

- **GIVEN** a user query "Какие водоемы с высоким приоритетом в Улытауском регионе?"
- **WHEN** POST /ai/chat with query and language="ru"
- **THEN** response SHALL include: natural language answer, list of matching water objects with IDs and priorities

#### Scenario: Follow-up question with context

- **GIVEN** previous conversation about specific region
- **WHEN** user asks "А сколько из них озера?"
- **THEN** agent SHALL understand context and filter previous results by resource_type="lake"

#### Scenario: Handle ambiguous queries

- **GIVEN** a vague query without clear filters
- **WHEN** agent processes query
- **THEN** response SHALL either ask clarifying questions or provide general information with caveats

### Requirement: Priority Explanation Endpoint

The system SHALL provide AI-powered explanations of inspection priorities for specific water objects.

#### Scenario: Explain high priority object

- **GIVEN** a water object with high priority (score 14)
- **WHEN** POST /ai/objects/5/explain-priority with language="ru"
- **THEN** response SHALL include: technical_condition justification, passport age analysis, priority formula breakdown, natural language explanation in 2-4 sentences

#### Scenario: Include passport context in explanation

- **GIVEN** a water object with passport containing degradation details
- **WHEN** requesting priority explanation
- **THEN** explanation SHALL reference specific passport findings (e.g., "высокая степень зарастания")

#### Scenario: Expert-only access

- **GIVEN** a user with role="guest"
- **WHEN** attempting to access /ai/objects/{id}/explain-priority
- **THEN** 403 Forbidden SHALL be returned

### Requirement: Natural Language Search Endpoint

The system SHALL provide semantic search across water objects and passport documents.

#### Scenario: Search by characteristics

- **GIVEN** a query "Озера с непресной водой и высокой рыбопродуктивностью в Улытауском районе"
- **WHEN** POST /ai/search with query
- **THEN** agent SHALL: classify search intent, apply SQL filters, search passport text, return structured results with summaries

#### Scenario: Keyword-based passport search

- **GIVEN** passport documents with term "рыбопродуктивность"
- **WHEN** searching for that term
- **THEN** objects with matching passport text SHALL be returned with relevant excerpts

#### Scenario: Combine structured and semantic search

- **GIVEN** a query mixing database fields and text search
- **WHEN** agent processes search
- **THEN** both SQL filtering and vector/text search SHALL be used

#### Scenario: Return search confidence

- **GIVEN** search results
- **WHEN** formatting response
- **THEN** each result SHALL include relevance score or confidence indicator

### Requirement: Domain-Specific Response Formatting

The system SHALL format AI responses with water management terminology and structure.

#### Scenario: Use technical terms correctly

- **GIVEN** a response about water bodies
- **WHEN** generating text
- **THEN** terminology SHALL match domain standards (озеро/водохранилище/канал, пресная/непресная вода, etc.)

#### Scenario: Structure complex responses

- **GIVEN** a query returning multiple objects
- **WHEN** formatting response
- **THEN** information SHALL be organized by region, priority, or other logical grouping

#### Scenario: Include quantitative data

- **GIVEN** information about water objects
- **WHEN** generating response
- **THEN** relevant numbers SHALL be included (priority scores, counts, coordinates)

### Requirement: Error Handling for AI Queries

The system SHALL gracefully handle errors and edge cases in AI endpoints.

#### Scenario: Handle non-existent object ID

- **GIVEN** a request to /ai/objects/9999/explain-priority
- **WHEN** object 9999 does not exist
- **THEN** 404 Not Found SHALL be returned with helpful message

#### Scenario: Handle Gemini API failure

- **GIVEN** Gemini API is unavailable
- **WHEN** processing AI query
- **THEN** 503 Service Unavailable SHALL be returned with retry guidance

#### Scenario: Handle timeout on complex queries

- **GIVEN** a query requiring extensive processing
- **WHEN** max agent iterations reached
- **THEN** partial response SHALL be returned with indication of incomplete analysis

### Requirement: Query Language Support

The system SHALL support queries in Russian with Russian responses.

#### Scenario: Process Russian input

- **GIVEN** a query in Russian
- **WHEN** analyzing intent and extracting entities
- **THEN** natural language processing SHALL correctly parse Russian text

#### Scenario: Generate Russian output

- **GIVEN** query results
- **WHEN** generating final response
- **THEN** output SHALL be grammatically correct Russian with proper technical terminology

### Requirement: Response Caching for Common Queries

The system SHALL cache responses for frequently asked questions to reduce API costs.

#### Scenario: Cache regional summaries

- **GIVEN** a query about all objects in a region
- **WHEN** same query is made within 1 hour
- **THEN** cached response SHALL be returned without LLM call

#### Scenario: Invalidate cache on data changes

- **GIVEN** cached responses exist
- **WHEN** water object data is updated
- **THEN** relevant cached responses SHALL be invalidated
