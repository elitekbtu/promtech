# RAG System Specification

## MODIFIED Requirements

### Requirement: Domain-Specific System Prompts

The RAG system SHALL use water management and hydro-engineering domain knowledge in system prompts.

**Previous**: Generic RAG system prompts for general knowledge queries.  
**Change**: Specialized prompts for water resource management in Kazakhstan.

#### Scenario: RAG agent understands water domain

- **GIVEN** a user query about water objects
- **WHEN** RAG agent processes the query
- **THEN** system prompt SHALL identify agent as "помощник по гидротехническим сооружениям и водным ресурсам Казахстана"

#### Scenario: RAG uses available tools

- **GIVEN** a query requiring water object data
- **WHEN** RAG agent analyzes query
- **THEN** agent SHALL know it has access to: search_water_objects, get_passport_content, explain_priority_logic tools

#### Scenario: RAG stays within domain knowledge

- **GIVEN** a query about water management
- **WHEN** generating response
- **THEN** RAG SHALL answer based only on available data and honestly state when information is insufficient

## ADDED Requirements

### Requirement: Water Object Search Tool

The RAG system SHALL provide a tool for searching and filtering water objects.

#### Scenario: Search by region

- **GIVEN** a RAG query mentioning a specific region
- **WHEN** agent invokes search_water_objects tool with region filter
- **THEN** matching water objects SHALL be returned with key attributes

#### Scenario: Search by resource type

- **GIVEN** a query about "озера" (lakes)
- **WHEN** agent invokes search_water_objects with resource_type="lake"
- **THEN** only lake objects SHALL be returned

#### Scenario: Search by priority level

- **GIVEN** a query about high-priority objects
- **WHEN** agent invokes search_water_objects with priority_level="high"
- **THEN** objects with high priority SHALL be returned sorted by priority score

#### Scenario: Limit search results

- **GIVEN** a broad search query
- **WHEN** agent invokes search_water_objects
- **THEN** at most 10 results SHALL be returned by default to avoid context overflow

### Requirement: Passport Content Retrieval Tool

The RAG system SHALL provide a tool for retrieving passport document text.

#### Scenario: Get full passport content

- **GIVEN** a query about specific water object characteristics
- **WHEN** agent invokes get_passport_content for that object
- **THEN** all passport sections SHALL be returned as structured text

#### Scenario: Get specific sections

- **GIVEN** a query about biological characteristics
- **WHEN** agent invokes get_passport_content with sections=["biological"]
- **THEN** only biological section text SHALL be returned

#### Scenario: Handle missing passport

- **GIVEN** a water object without passport
- **WHEN** agent invokes get_passport_content
- **THEN** tool SHALL return indication that no passport exists

### Requirement: Priority Explanation Tool

The RAG system SHALL provide a tool for explaining inspection priority calculations.

#### Scenario: Explain priority components

- **GIVEN** a query about why an object has specific priority
- **WHEN** agent invokes explain_priority_logic
- **THEN** response SHALL include: technical_condition value, passport_age_years, priority formula breakdown, final score and level

#### Scenario: Generate human-readable explanation

- **GIVEN** priority calculation components
- **WHEN** formatting explanation
- **THEN** response SHALL be in natural Russian language explaining urgency factors

### Requirement: Vector Store with Passport Documents

The RAG system SHALL index passport document text in vector database for semantic search.

#### Scenario: Index passport on upload

- **GIVEN** a passport PDF is uploaded and text extracted
- **WHEN** saving to database
- **THEN** text SHALL be embedded and indexed in ChromaDB/FAISS

#### Scenario: Semantic search across passports

- **GIVEN** a natural language query about water characteristics
- **WHEN** performing vector search
- **THEN** relevant passport sections SHALL be retrieved by semantic similarity

#### Scenario: Combine vector and SQL search

- **GIVEN** a query with both structured filters and semantic content
- **WHEN** agent processes query
- **THEN** both search_water_objects (SQL) and vector_search (semantic) tools SHALL be used together

### Requirement: Context Management for Water Queries

The RAG system SHALL maintain conversation context relevant to water management.

#### Scenario: Remember previous object references

- **GIVEN** a conversation about a specific water object
- **WHEN** user asks follow-up question
- **THEN** agent SHALL recall object context from conversation history

#### Scenario: Aggregate information across objects

- **GIVEN** a query about regional trends
- **WHEN** agent gathers data from multiple objects
- **THEN** information SHALL be synthesized into coherent summary

### Requirement: Source Citation for Water Data

The RAG system SHALL cite sources when providing information about water objects.

#### Scenario: Cite water object database

- **GIVEN** information from water_objects table
- **WHEN** generating response
- **THEN** response SHALL include object IDs and names as sources

#### Scenario: Cite passport documents

- **GIVEN** information from passport text
- **WHEN** generating response
- **THEN** response SHALL indicate information came from passport and which section

### Requirement: Confidence Scoring for Water Queries

The RAG system SHALL provide confidence scores for responses about water management.

#### Scenario: High confidence with direct data

- **GIVEN** a query answered directly from water_objects table
- **WHEN** generating response
- **THEN** confidence score SHALL be >= 0.9

#### Scenario: Lower confidence with inferred data

- **GIVEN** a query requiring interpretation of passport text
- **WHEN** generating response
- **THEN** confidence score SHALL reflect uncertainty (0.6-0.8 range)

### Requirement: Multi-Language Query Support

The RAG system SHALL handle queries in Russian and provide Russian responses.

#### Scenario: Process Russian query

- **GIVEN** a query in Russian about water objects
- **WHEN** agent processes query
- **THEN** understanding and tool invocation SHALL work correctly

#### Scenario: Generate Russian response

- **GIVEN** query results from tools
- **WHEN** generating final response
- **THEN** response SHALL be in fluent Russian matching domain terminology
