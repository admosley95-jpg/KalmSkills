# Project Strategy: Comprehensive Resume & Job Matching Database

This document outlines the strategy for scaling the prototype to a comprehensive database, as described in the project initialization.

## 1. The Prototype (ResumeJobMatcher.jsx)

The current prototype simulates the core logic:

*   **ATS Parser Simulation**: Client-side engine scanning resume text for keywords (Hard/Soft skills).
*   **O*NET-Style Database**: Structured database of jobs and their required skill taxonomies (Hard vs Soft Skills).
*   **Gap Analysis**: Visual mapping of skills possessed vs. skills required.
*   **Match Scoring**: Percentage match based on weighted skill overlap.
*   **Market Context**: Integration of simulated SEC 10-K signals for hiring intent.

## 2. The Strategy & Data Guide

To scale this to a "Comprehensive Database" using LinkedIn, SEC, O*NET, Burning Glass Institute, and other open source data, the following strategy is proposed:

### Legal & Ethical Considerations
*   **Scraping**: Avoid unauthorized scraping of LinkedIn or Burning Glass. Use official APIs where available.
*   **Compliance**: Adhere to terms of service and data privacy laws (GDPR, CCPA).

### Data Sources
*   **O*NET**: Use the official O*NET database for standardized job descriptions and skill taxonomies.
*   **Lightcast Open Skills**: Leverage open-source skill taxonomies for normalization.
*   **SEC 10-K/10-Q Filings**:
    *   **Method**: Use NLP to extract "Forward-Looking Statements" and "Risk Factors" from EDGAR filings.
    *   **Goal**: Identify hiring trends, R&D expansion, or budget constraints (as simulated in the prototype).

### Implementation Steps (Future Work)
1.  **Backend Integration**: Move the taxonomy and matching logic to a backend (e.g., Python/Django or Node.js).
2.  **Database**: Use PostgreSQL or Elasticsearch to store the comprehensive skill graph.
3.  **Data Pipeline**: Build pipelines to ingest O*NET data and process SEC filings.
4.  **API Integration**: Connect to legitimate job board APIs (Indeed, LinkedIn if available, etc.) instead of scraping.
