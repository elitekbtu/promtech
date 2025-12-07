# Passport Management Specification

## ADDED Requirements

### Requirement: Passport Document Storage

The system SHALL store PDF passport documents for water objects and provide access via URL.

#### Scenario: Upload passport PDF

- **GIVEN** a water object with id=5
- **WHEN** uploading a passport PDF file
- **THEN** file SHALL be stored at {FILE_STORAGE_PATH}/passports/5.pdf and pdf_url SHALL be set to {FILE_STORAGE_BASE_URL}/passports/5.pdf

#### Scenario: Access passport via URL

- **GIVEN** a water object with pdf_url set
- **WHEN** accessing the URL
- **THEN** the PDF file SHALL be returned for download

#### Scenario: Handle missing passport

- **GIVEN** a water object with no passport document
- **WHEN** requesting GET /objects/{id}/passport
- **THEN** response SHALL indicate exists=false

### Requirement: Passport Text Extraction

The system SHALL extract text content from passport PDFs for searchability and AI analysis.

#### Scenario: Extract text on upload

- **GIVEN** a passport PDF being uploaded
- **WHEN** file is saved
- **THEN** text SHALL be extracted using pypdf and stored in passport_texts table

#### Scenario: Store text by sections

- **GIVEN** extracted passport text
- **WHEN** saving to database
- **THEN** text SHALL be organized by sections: physical, biological, productivity

#### Scenario: Retrieve passport text by section

- **GIVEN** a water object with passport text
- **WHEN** requesting specific sections
- **THEN** only requested section text SHALL be returned

### Requirement: Passport Metadata

The system SHALL provide metadata about passport documents without requiring full download.

#### Scenario: Get passport metadata

- **GIVEN** a water object with passport
- **WHEN** requesting GET /objects/{id}/passport
- **THEN** response SHALL include: exists=true, pdf_url, and passport_date

#### Scenario: Passport existence check

- **GIVEN** any water object
- **WHEN** checking passport availability
- **THEN** system SHALL quickly determine if passport exists without file I/O

### Requirement: Passport Search Integration

The system SHALL make passport text searchable for filtering and RAG queries.

#### Scenario: Search across passport text

- **GIVEN** multiple water objects with passport text
- **WHEN** searching for term "рыбопродуктивность"
- **THEN** objects with that term in any passport section SHALL be identified

#### Scenario: Section-specific search

- **GIVEN** passport text organized by sections
- **WHEN** searching within "biological" section only
- **THEN** only matches in biological sections SHALL be returned

### Requirement: Passport File Validation

The system SHALL validate uploaded passport files for format and size.

#### Scenario: Accept PDF files

- **GIVEN** a file upload with content-type="application/pdf"
- **WHEN** validating file
- **THEN** file SHALL be accepted

#### Scenario: Reject non-PDF files

- **GIVEN** a file upload with content-type other than PDF
- **WHEN** validating file
- **THEN** 400 Bad Request SHALL be returned with error message

#### Scenario: Enforce file size limit

- **GIVEN** a PDF file larger than 10MB
- **WHEN** attempting upload
- **THEN** 413 Payload Too Large SHALL be returned

### Requirement: Passport Update and Versioning

The system SHALL handle passport document updates while preserving history.

#### Scenario: Update passport document

- **GIVEN** a water object with existing passport
- **WHEN** uploading new passport PDF
- **THEN** old file SHALL be replaced and passport_date SHALL be updated

#### Scenario: Update triggers priority recalculation

- **GIVEN** a water object with existing passport
- **WHEN** passport_date is updated
- **THEN** priority score SHALL be automatically recalculated

### Requirement: Bulk Passport Processing

The system SHALL support batch processing of passport documents for initial data load.

#### Scenario: Import multiple passports

- **GIVEN** a directory of PDF files named by object_id
- **WHEN** running bulk import script
- **THEN** each file SHALL be processed and associated with corresponding water object
