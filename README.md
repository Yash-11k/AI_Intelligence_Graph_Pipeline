# 🚀 FrontierAtlas — AI Intelligence Pipeline

**FrontierAtlas** is an end-to-end AI Intelligence Pipeline built to collect, process, clean, and organize information from the AI ecosystem.

The pipeline collects data across **5 major verticals**:

* 🏢 AI Startups
* 🛠️ AI Products & Tools
* 📄 Research Papers
* 💼 AI/ML Jobs
* 📰 AI News

The main goal was not just to scrape data, but to build a pipeline that can handle **messy web data, rate limits, duplicate entities, invalid LLM outputs, and stale information** without breaking the entire system.

---

## 📊 Live Data & Deliverables

### Google Sheets Data Hub

The processed data is available in a 6-tab Google Sheets data hub:

**[FrontierAtlas Public Data Hub](https://docs.google.com/spreadsheets/d/1hE0AIYUm3UZ9BK6fFFNzjcSfJceHsUW9nEu_k5ruj3A/edit?usp=sharing)**

The sheets contain:

1. Startups
2. Products
3. Research Papers
4. Jobs
5. News
6. Entity Mapping Log

### Architecture Documentation

The repository also contains:

`output/architecture.pdf`

This document explains the complete pipeline architecture, data flow, technical choices, and scalability approach.

---

# 🧠 What is FrontierAtlas?

The internet contains a huge amount of AI-related information, but the data is usually:

* spread across different websites
* stored in different formats
* duplicated under different names
* updated at different times
* sometimes incomplete or inconsistent

For example:

```text
OpenAI Inc.
Open AI
OpenAI
OpenAI Labs
```

A simple scraper can treat these as separate entities.

Similarly, a news website might publish:

```text
"2 hours ago"
```

while another source provides:

```text
2026-09-15T14:30:00Z
```

FrontierAtlas converts these different formats into a **common structured format** so the final data can be analyzed consistently.

---

# 🏗️ System Architecture

The pipeline is divided into four major stages:

```text
                 ┌──────────────────────────────┐
                 │       Web / APIs / Feeds     │
                 │                              │
                 │ YC API                       │
                 │ AI Tools List                │
                 │ Semantic Scholar             │
                 │ RSS Feeds                    │
                 │ RemoteOK                      │
                 └──────────────┬───────────────┘
                                │
                                ▼
                 ┌──────────────────────────────┐
                 │   Acquisition & Ingestion    │
                 │                              │
                 │ Async Scrapers               │
                 │ aiohttp / Requests           │
                 │ RSS / API ingestion          │
                 │ Concurrency Control          │
                 └──────────────┬───────────────┘
                                │
                                ▼
                 ┌──────────────────────────────┐
                 │     LLM Extraction Layer    │
                 │                              │
                 │ Groq API                    │
                 │ Primary Model               │
                 │        ↓                     │
                 │ Fallback Model              │
                 │        ↓                     │
                 │ Safe Default                │
                 └──────────────┬───────────────┘
                                │
                                ▼
                 ┌──────────────────────────────┐
                 │   Entity Resolution Engine  │
                 │                              │
                 │ Normalization               │
                 │ Legal Suffix Removal        │
                 │ RapidFuzz Matching           │
                 │ Canonical Seed List          │
                 └──────────────┬───────────────┘
                                │
                                ▼
                 ┌──────────────────────────────┐
                 │       Output & Delivery      │
                 │                              │
                 │ CSV Files                   │
                 │ Entity Mapping Logs         │
                 │ Google Sheets               │
                 └──────────────────────────────┘
```

---

# 🔥 Key Features

## 1. Multi-Source Data Collection

FrontierAtlas does not depend on a single website.

Different sources are used for different types of information.

| Vertical        | Source                          | Purpose                          |
| --------------- | ------------------------------- | -------------------------------- |
| Startups        | Y Combinator public company API | AI startup/company information   |
| Products        | AI-Tools-List                   | AI tools and product information |
| Research Papers | Semantic Scholar                | Research paper metadata          |
| News            | RSS feeds                       | Recent AI news                   |
| Jobs            | RSS feeds + RemoteOK            | AI/ML/Data job listings          |

This makes the pipeline more flexible and reduces dependency on a single source.

---

# 🏢 Startup Data

For startup information, the pipeline uses the **Y Combinator public company API**.

The source provides structured information about thousands of companies and also provides legitimate company URLs.

The pipeline extracts and normalizes the useful fields into a common startup schema.

Example:

```json
{
  "startupName": "Example AI",
  "description": "AI-powered enterprise platform",
  "website": "https://example.com"
}
```

---

# 🛠️ AI Product Data

The product pipeline uses the **AI-Tools-List** dataset as one of the primary sources.

The dataset contains thousands of AI tools.

One challenge was that some fields, such as pricing model, are not directly available in a clean structured format.

For example, a description might say:

```text
Free plan available with premium features.
```

The LLM extraction layer can convert this into a structured value such as:

```text
FREEMIUM
```

This allows unstructured descriptions to become usable structured data.

---

# 📄 Research Paper Data

Research papers are collected using the **Semantic Scholar Bulk/API ecosystem**.

The pipeline extracts relevant paper metadata and converts it into the common output schema.

Typical information includes:

* Paper title
* Authors
* Abstract
* Publication information
* URL
* Research-related metadata

### Why Semantic Scholar?

During testing, the legacy arXiv export API showed intermittent `503` responses.

Instead of making the entire pipeline dependent on an unreliable endpoint, Semantic Scholar was used as the primary research source.

This was an intentional engineering trade-off rather than silently ignoring the problem.

---

# 📰 News Intelligence

News is collected from multiple RSS feeds.

Current sources include feeds such as:

* TechCrunch AI
* VentureBeat
* MIT Technology Review
* Ars Technica
* Hacker News

The system focuses on **recent signals** instead of continuously accumulating stale articles.

---

# ⏱️ Strict 24-Hour Freshness Filter

One of the important parts of the news pipeline is timestamp normalization.

Different websites provide dates in different formats.

For example:

```text
2 hours ago
30 minutes ago
Yesterday
2026-09-15T12:30:00Z
```

Using `dateparser`, relative timestamps are converted into standardized datetime values.

Conceptually:

```text
"2 hours ago"
       ↓
Parsed datetime
       ↓
ISO UTC timestamp
       ↓
24-hour cutoff check
       ↓
Fresh / Stale
```

Only records inside the defined freshness window are allowed into the final signal dataset.

This prevents old news and job listings from being treated as current intelligence.

---

# 💼 Jobs Intelligence

The job pipeline combines multiple sources, including:

* RSS feeds
* RemoteOK API fallback

The pipeline applies keyword-based filtering to focus on relevant roles such as:

```text
AI
ML
Machine Learning
Data Science
Data Analyst
AI Engineer
```

The final records are normalized into the common schema.

---

# ⚡ LLM Extraction Layer

Scraped data is often not structured enough to directly store in a clean dataset.

This is where the LLM extraction layer comes in.

The pipeline uses the **Groq API** for structured extraction and includes fallback handling so that one failed model request does not automatically kill the pipeline.

The extraction flow is conceptually:

```text
Raw Description
      │
      ▼
Primary LLM
      │
      ├── Valid JSON ─────────► Continue
      │
      └── Error / Invalid JSON
                  │
                  ▼
             Fallback LLM
                  │
                  ├── Valid ──► Continue
                  │
                  └── Failed
                         │
                         ▼
                    Safe Default
```

---

# 🔄 LLM Fallback & Error Handling

External LLM APIs can fail for several reasons:

* HTTP `429` rate limits
* HTTP `413` payload too large
* temporary API failures
* invalid JSON responses
* unexpected model output

Instead of allowing these errors to crash the pipeline, retry and fallback logic is used.

### 429 Rate Limits

The pipeline uses exponential backoff with jitter.

Conceptually:

```text
Request
   ↓
429?
   ↓
Wait 2s
   ↓
Retry
   ↓
429?
   ↓
Wait 4s
   ↓
Retry
   ↓
Wait 8s...
```

This reduces unnecessary pressure on the API and gives temporary rate limits time to recover.

---

# 📦 413 Context / Payload Protection

Large descriptions can cause context or payload problems.

To avoid sending unnecessarily large product descriptions to the LLM, the input is truncated before extraction.

Example:

```python
description = description[:500]
```

This keeps the extraction request small while retaining enough information for basic classification.

---

# 🛡️ Safe Defaults

A pipeline should not lose an entire record because one optional LLM extraction failed.

If the extraction fails or both model attempts return invalid output, a safe default is used where appropriate.

For example:

```text
Unknown pricing information
        ↓
LLM extraction fails
        ↓
FREEMIUM / Safe Default
```

The important part is that the pipeline continues processing instead of silently dropping the entire record.

---

# 🧠 Entity Resolution

Entity resolution was one of the more interesting parts of this project.

The same company can appear under different names:

```text
OpenAI Inc
Open AI
OpenAI
```

while completely different companies can share common words:

```text
C3 AI
Pretzel AI
```

A naive fuzzy matcher can incorrectly merge unrelated companies simply because they both contain `"AI"`.

---

# 🔍 Entity Resolution Strategy

The pipeline uses a **two-stage matching approach**.

### Stage 1 — Exact Normalization

First, the raw entity name is cleaned.

The process includes:

* lowercase conversion
* whitespace normalization
* legal suffix removal
* punctuation normalization

Examples:

```text
OpenAI Inc.
      ↓
openai
```

```text
Open AI LLC
      ↓
open ai
```

---

### Stage 2 — Fuzzy Matching

After normalization, the cleaned name is compared against a canonical seed list using **RapidFuzz**.

A similarity threshold is applied before accepting a match.

The pipeline uses character-level similarity to reduce false matches caused by generic words.

Example:

```text
Open AI
   ↓
open ai
   ↓
RapidFuzz comparison
   ↓
OpenAI
```

But:

```text
Pretzel AI
   ↓
pretzel ai
   ↓
C3 AI
   ↓
Rejected
```

This approach was chosen after testing different fuzzy matching strategies.

---

# 📋 Canonical Entity Seed List

The project maintains a seed list containing known canonical AI company names.

Current design:

```text
50 known canonical AI companies
```

The raw entity is compared against this list and mapped to the canonical representation when a valid match is found.

---

# 🧾 Entity Mapping Log

Entity resolution decisions are logged instead of silently changing the original data.

The mapping log records information such as:

```text
Raw Entity
     ↓
Normalized Entity
     ↓
Canonical Entity
     ↓
Match / Decision
```

This makes the system easier to debug and audit.

Output:

```text
output/entity_mapping_log.csv
```

---

# 🚀 Async Data Ingestion

The scrapers are designed around asynchronous execution where applicable.

Instead of processing every request sequentially:

```text
Request 1 → Wait → Finish
Request 2 → Wait → Finish
Request 3 → Wait → Finish
```

the pipeline can process multiple requests concurrently:

```text
        ┌── Request 1
        ├── Request 2
Input ──┼── Request 3
        ├── Request 4
        └── Request 5
```

Concurrency is controlled using:

```python
asyncio.Semaphore
```

This allows the pipeline to improve throughput without creating an uncontrolled number of simultaneous requests.

---

# 🔐 Retry & Resilience

External services are unreliable by nature.

The pipeline therefore uses retry/backoff logic around external calls where appropriate.

The basic strategy is:

```text
External Request
      ↓
Success?
 ┌────┴────┐
Yes       No
 ↓         ↓
Continue  Retry
            ↓
       Backoff
            ↓
         Retry
            ↓
       Fallback
```

The objective is simple:

**A temporary external failure should not automatically become a complete pipeline failure.**

---

# 📊 Canonical Output Schema

The different sources produce different formats.

FrontierAtlas converts them into structured datasets that can be consumed by downstream systems.

The final output is divided into:

```text
startups.csv
products.csv
papers.csv
jobs.csv
news.csv
entity_mapping_log.csv
```

This separation makes the datasets easier to inspect and use independently.

---

# 📁 Project Structure

```text
AI_Pipeline/
│
├── README.md
├── requirements.txt
├── .env.example
│
├── architecture.pdf
│
├── src/
│   ├── paper_scraper.py
│   ├── save_papers.py
│   ├── startup_scraper.py
│   ├── product_scraper.py
│   ├── llm_extractor.py
│   ├── entity_resolver.py
│   ├── news_jobs_scraper.py
│   ├── github_helper.py
│   └── generate_pdf.py
│
└── output/
    ├── startups.csv
    ├── products.csv
    ├── papers.csv
    ├── jobs.csv
    ├── news.csv
    ├── entity_mapping_log.csv
    └── architecture.pdf
```

---

# 🛠️ Tech Stack

### Programming

* Python
* AsyncIO

### Data Collection

* aiohttp
* Requests
* RSS / Feedparser
* API-based ingestion
* Web scraping tools where required

### AI / LLM

* Groq API
* LLM-based structured extraction
* JSON validation
* Fallback handling

### Data Processing

* Pandas
* RapidFuzz
* Dateparser

### Output

* CSV
* Google Sheets
* ReportLab PDF documentation

### Reliability

* Tenacity
* Exponential backoff
* Jitter
* Concurrency control

---

# ⚙️ Technical Design Decisions

## Why Async?

The pipeline is network-heavy.

Most of the time is spent waiting for:

* APIs
* RSS feeds
* web responses
* LLM responses

Async execution allows multiple independent operations to progress without waiting for each one sequentially.

---

## Why RapidFuzz?

Entity resolution requires comparing names efficiently.

RapidFuzz provides fast fuzzy string matching while keeping the implementation lightweight.

The important part is not simply using fuzzy matching, but combining it with:

```text
Normalization
+
Legal suffix removal
+
Threshold
+
Canonical seed list
```

This reduces accidental matches.

---

## Why LLM Extraction?

Some source data is semi-structured or completely unstructured.

For example:

```text
"Start with our free plan. Teams can upgrade
to the Pro version for additional features."
```

A traditional parser may struggle to consistently identify:

```text
pricing_model = FREEMIUM
```

The LLM is used as an extraction layer to convert this kind of information into structured fields.

---

# 🗄️ Future Database Architecture

The current submission produces CSV datasets and a Google Sheets data hub.

For a larger production deployment, the same pipeline can be extended with a proper database architecture.

### Graph Database

A graph database such as **Neo4j** could represent relationships such as:

```text
Startup
   │
   ├── Founder
   │
   ├── Product
   │
   ├── Funding
   │
   └── Research Paper
```

This would make relationship-based queries easier.

For example:

```text
Which AI startups are connected to
a particular research area?
```

---

### Vector Database

A vector database such as **Pinecone** could be used for semantic search across:

* research paper abstracts
* job descriptions
* startup descriptions
* product descriptions

This would enable queries based on meaning rather than exact keywords.

Example:

```text
"Find AI companies working on
automated drug discovery"
```

could retrieve semantically relevant companies even when those exact words are not present.

---

# 📈 Scalability

The demo task was developed under a limited implementation timeline, so the current submission focuses on achieving the required dataset coverage and demonstrating the architecture.

The initial target was approximately **1,000+ records** across the required categories.

The architecture is designed so that individual ingestion modules can be scaled independently.

For example:

```text
Startup Scraper ─────┐
                     │
Product Scraper ────┤
                     ├──► Processing Layer
Paper Scraper ──────┤
                     │
News Scraper ───────┤
                     │
Jobs Scraper ───────┘
```

Because the ingestion modules are relatively independent and stateless, they can be distributed across multiple workers in a larger deployment.

The architecture can therefore be extended toward much larger datasets without completely rewriting the pipeline.

---

# ⚠️ Known Limitations & Trade-offs

No data pipeline is perfect, especially when built against external public sources.

The following limitations were identified during development.

### 1. Dataset Scale

Because of the short development timeline, the submission focused on the required minimum dataset rather than attempting to process hundreds of thousands of records during the demo.

The architecture itself is designed with pagination, asynchronous ingestion, and independent scraper modules so that processing can be expanded later.

### 2. External API Reliability

Some public APIs can return temporary errors.

During testing, the legacy arXiv export API returned intermittent `503` responses.

Semantic Scholar was therefore selected as the primary research-paper source.

### 3. Product Entity Naming

The product source does not always clearly separate the company behind a tool from the product itself.

For those records, the tool's name is used as the `startupName` field where necessary.

This is a documented simplification based on the available source data.

### 4. Entity Matching

Fuzzy matching can never guarantee perfect entity resolution across every possible company name.

The system therefore combines fuzzy matching with normalization and a canonical seed list instead of relying on similarity alone.

---

# 🔧 Local Setup

## 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd AI_Pipeline
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

A sample environment file is also included:

```text
.env.example
```

**Do not commit your real API key to GitHub.**

---

# ▶️ Running the Pipeline

Move into the source directory:

```bash
cd src
```

Then run the required pipeline stages.

### Research Papers

```bash
python paper_scraper.py
python save_papers.py
```

### Startups

```bash
python startup_scraper.py
```

### Products

```bash
python product_scraper.py
```

### Entity Resolution

```bash
python entity_resolver.py
```

### News & Jobs

```bash
python news_jobs_scraper.py
```

### Architecture PDF

```bash
python generate_pdf.py
```

---

# 📦 Requirements

The main dependencies include:

```text
aiohttp
asyncio
pandas
rapidfuzz
feedparser
dateparser
tenacity
requests
python-dotenv
reportlab
```

The complete environment can be installed using:

```bash
pip install -r requirements.txt
```

---

# 🔄 Complete Pipeline Flow

The complete workflow can be summarized as:

```text
        DATA SOURCES
             │
             ▼
     ┌───────────────┐
     │ Data Ingestion │
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐
     │ Async Fetching │
     └───────┬───────┘
             │
             ▼
     ┌────────────────┐
     │ Data Cleaning  │
     │ & Normalizing  │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ LLM Extraction │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ JSON Validation │
     │ + Fallbacks     │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ Entity         │
     │ Resolution     │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ Freshness      │
     │ Filtering      │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ CSV Outputs    │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ Google Sheets  │
     └────────────────┘
```

---

# 🎯 What I Learned From This Project

The biggest learning from FrontierAtlas was that **data collection is only one part of building an intelligence pipeline**.

The difficult parts are what happen after collection:

```text
Bad API response
       ↓
Rate limit
       ↓
Retry
       ↓
Invalid LLM output
       ↓
Fallback
       ↓
Duplicate entity
       ↓
Entity resolution
       ↓
Stale signal
       ↓
Freshness filter
       ↓
Clean structured dataset
```

Building a scraper that works once is relatively easy.

Building a pipeline that can **handle failure, messy data, inconsistent names, and changing external sources** is where the real engineering challenge starts.

---

# 🚀 Future Improvements

Some possible improvements for the next version include:

* Distributed scraping workers
* PostgreSQL / production database integration
* Neo4j graph-based entity relationships
* Vector database for semantic search
* Automated Google Sheets synchronization
* Better entity resolution using learned embeddings
* More data sources
* Continuous scheduled ingestion
* Monitoring and alerting
* Dockerized production deployment
* API layer for querying the intelligence dataset
* Dashboard for real-time AI ecosystem signals

---

# 📊 Project Outputs

The final pipeline generates:

```text
startups.csv
products.csv
papers.csv
jobs.csv
news.csv
entity_mapping_log.csv
architecture.pdf
```

These datasets can then be used for:

* AI ecosystem analysis
* market intelligence
* startup discovery
* AI product research
* research trend analysis
* job-market monitoring
* downstream analytics and dashboards

---

# 👨‍💻 Author

**Yash**

AI / Data Engineering Enthusiast

Built as part of the **AI Engineer Demo Task — GraphOne / FrontierAtlas**.

---

# 📜 License

This project is licensed under the **MIT License**.
