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
- **THEN** agent SHALL know it has access to existing vector_search and web_search tools with water-specific indexed content

#### Scenario: RAG stays within domain knowledge

- **GIVEN** a query about water management
- **WHEN** generating response
- **THEN** RAG SHALL answer based only on available data and honestly state when information is insufficient

## ADDED Requirements

### Requirement: Vector Store with Water Management Data

The RAG system SHALL index water management data including passport documents, object metadata, and priority information in the vector database for semantic search.

#### Scenario: Index passport on upload

- **GIVEN** a passport PDF is uploaded and text extracted
- **WHEN** saving to database
- **THEN** text SHALL be embedded and indexed in ChromaDB/FAISS with metadata (object_id, object_name, region, resource_type, sections)

#### Scenario: Index water object structured data

- **GIVEN** water objects with all attributes
- **WHEN** initializing vector store
- **THEN** object information SHALL be formatted as searchable text documents including: name, region, resource type, water type, fauna, technical condition, priority level, passport date

#### Scenario: Semantic search across all water data

- **GIVEN** a natural language query about water characteristics or priorities
- **WHEN** performing vector_search
- **THEN** relevant content SHALL be retrieved from both passport text and structured object data by semantic similarity

#### Scenario: Priority explanation via vector search

- **GIVEN** a query about why an object has specific priority
- **WHEN** performing vector_search
- **THEN** indexed documents SHALL include priority calculation explanation text with formula breakdown and factors

#### Scenario: Regional and type-specific search

- **GIVEN** a query about specific region or resource type
- **WHEN** vector_search retrieves results
- **THEN** metadata filtering SHALL narrow results to relevant objects before semantic ranking

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

The RAG system SHALL cite sources when providing information about water objects using metadata from vector search results.

#### Scenario: Cite water object from vector search

- **GIVEN** information retrieved via vector_search
- **WHEN** generating response
- **THEN** response SHALL include object IDs, names, and regions from document metadata

#### Scenario: Cite passport documents from vector search

- **GIVEN** information from passport text via vector_search
- **WHEN** generating response
- **THEN** response SHALL indicate information came from passport with object name and section (from metadata)

### Requirement: Confidence Scoring for Water Queries

The RAG system SHALL provide confidence scores for responses about water management.

#### Scenario: High confidence with direct data

- **GIVEN** a query answered directly from indexed water object data
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

- **GIVEN** query results from vector_search
- **WHEN** generating final response
- **THEN** response SHALL be in fluent Russian matching domain terminology
