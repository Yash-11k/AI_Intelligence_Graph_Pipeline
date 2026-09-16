"""
FrontierAtlas System Architecture Documentation

Generates a professional 3-page architecture and production design
document using ReportLab.
"""

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


OUTPUT_PATH = "architecture.pdf"


def build_pdf():
    os.makedirs("../output", exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=10,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=7,
    )

    subheading_style = ParagraphStyle(
        "SubHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=6,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-6,
        spaceAfter=4,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=body_style,
        fontSize=8.5,
        leading=11.5,
    )

    story = []

    # ============================================================
    # PAGE 1
    # ============================================================

    story.append(
        Paragraph(
            "FrontierAtlas: AI Data Intelligence Pipeline Architecture",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "<b>Author:</b> Yash &nbsp; | &nbsp; "
            "<b>System Specification:</b> Version 1.0 &nbsp; | &nbsp; "
            "<b>Project:</b> GraphOne / FrontierAtlas Demo Task",
            body_style,
        )
    )

    story.append(Spacer(1, 8))

    # 1. Overview
    story.append(
        Paragraph("1. Executive System Overview", heading_style)
    )

    story.append(
        Paragraph(
            "FrontierAtlas is an end-to-end AI ecosystem intelligence pipeline "
            "designed to collect, extract, normalize, and structure information "
            "from multiple public sources. The current system covers five major "
            "verticals: AI startups, AI products, research papers, jobs, and news.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "The architecture separates data acquisition, LLM-based extraction, "
            "entity resolution, freshness filtering, and output delivery so that "
            "individual components can be improved or scaled independently.",
            body_style,
        )
    )

    # 2. Core Architecture
    story.append(
        Paragraph("2. Core Ingestion Pipeline", heading_style)
    )

    pipeline_data = [
        [
            Paragraph("<b>Layer</b>", small_style),
            Paragraph("<b>Components</b>", small_style),
            Paragraph("<b>Responsibility</b>", small_style),
        ],
        [
            Paragraph("<b>1. Acquisition</b>", small_style),
            Paragraph(
                "aiohttp, Requests, RSS/Feedparser, public APIs",
                small_style,
            ),
            Paragraph(
                "Collect startup, product, paper, job, and news data "
                "from multiple external sources.",
                small_style,
            ),
        ],
        [
            Paragraph("<b>2. Extraction</b>", small_style),
            Paragraph(
                "Groq API, LLM structured extraction",
                small_style,
            ),
            Paragraph(
                "Convert semi-structured or unstructured source content "
                "into consistent JSON-style fields.",
                small_style,
            ),
        ],
        [
            Paragraph("<b>3. Resolution</b>", small_style),
            Paragraph(
                "RapidFuzz, normalization, canonical seed list",
                small_style,
            ),
            Paragraph(
                "Resolve duplicate or differently formatted company "
                "names against canonical entities.",
                small_style,
            ),
        ],
        [
            Paragraph("<b>4. Validation</b>", small_style),
            Paragraph(
                "Dateparser, freshness rules, JSON validation",
                small_style,
            ),
            Paragraph(
                "Remove stale signals and validate extracted records "
                "before they reach the final dataset.",
                small_style,
            ),
        ],
        [
            Paragraph("<b>5. Delivery</b>", small_style),
            Paragraph(
                "Pandas, CSV, Google Sheets",
                small_style,
            ),
            Paragraph(
                "Produce structured datasets and a reviewer-friendly "
                "six-tab data hub.",
                small_style,
            ),
        ],
    ]

    table1 = Table(
        pipeline_data,
        colWidths=[105, 160, 275],
        repeatRows=1,
    )

    table1.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table1)
    story.append(Spacer(1, 10))

    # 3. Data Sources
    story.append(
        Paragraph("3. Data Sources", heading_style)
    )

    source_data = [
        [
            Paragraph("<b>Vertical</b>", small_style),
            Paragraph("<b>Primary Source</b>", small_style),
            Paragraph("<b>Purpose</b>", small_style),
        ],
        [
            Paragraph("Startups", small_style),
            Paragraph("Y Combinator public company data", small_style),
            Paragraph("Startup/company information and URLs.", small_style),
        ],
        [
            Paragraph("Products", small_style),
            Paragraph("AI-Tools-List", small_style),
            Paragraph("AI tools and product descriptions.", small_style),
        ],
        [
            Paragraph("Research", small_style),
            Paragraph("Semantic Scholar", small_style),
            Paragraph("Research paper metadata and abstracts.", small_style),
        ],
        [
            Paragraph("News", small_style),
            Paragraph("AI-focused RSS feeds", small_style),
            Paragraph("Recent AI ecosystem news signals.", small_style),
        ],
        [
            Paragraph("Jobs", small_style),
            Paragraph("RSS feeds + RemoteOK", small_style),
            Paragraph("AI, ML, Data Science, and related roles.", small_style),
        ],
    ]

    table2 = Table(
        source_data,
        colWidths=[100, 190, 250],
        repeatRows=1,
    )

    table2.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(table2)
    story.append(Spacer(1, 10))

    # 4. Freshness
    story.append(
        Paragraph("4. 24-Hour Freshness Filtering", heading_style)
    )

    story.append(
        Paragraph(
            "News and job signals are time-sensitive, so FrontierAtlas applies "
            "a strict rolling 24-hour freshness rule.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Date normalization:</b> dateparser converts relative values "
            "such as '2 hours ago' into standardized datetime values.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>UTC normalization:</b> timestamps are converted into a common "
            "UTC representation where source information permits.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Hard cutoff:</b> records older than the configured 24-hour "
            "window are excluded from the current signal dataset.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Deduplication:</b> source URLs can be used as deterministic "
            "record identifiers to avoid processing the same signal repeatedly.",
            bullet_style,
        )
    )

    story.append(PageBreak())

    # ============================================================
    # PAGE 2
    # ============================================================

    story.append(
        Paragraph(
            "5. Resilience and Failure Handling",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "External APIs and web sources can fail temporarily. FrontierAtlas "
            "therefore treats failures as expected conditions rather than assuming "
            "every request will succeed.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "<b>HTTP 429 — Rate Limit Handling</b>",
            subheading_style,
        )
    )

    story.append(
        Paragraph(
            "• External calls use retry logic with exponential backoff and jitter "
            "where supported.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• Async concurrency is controlled using asyncio.Semaphore so the "
            "pipeline does not intentionally create an uncontrolled request burst.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• The LLM extraction layer supports fallback execution when the "
            "primary model request fails or returns unusable output.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "<b>HTTP 413 — Payload / Context Protection</b>",
            subheading_style,
        )
    )

    story.append(
        Paragraph(
            "Large text fields are truncated before LLM processing where the "
            "full content is not required for the target extraction. For example, "
            "product descriptions can be restricted to a fixed character budget.",
            body_style,
        )
    )

    # 6. LLM Architecture
    story.append(
        Paragraph(
            "6. Multi-Tier LLM Extraction Architecture",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "The LLM layer converts unstructured descriptions into structured "
            "fields. The design avoids making the entire pipeline dependent on "
            "one successful model response.",
            body_style,
        )
    )

    llm_data = [
        [
            Paragraph("<b>Tier</b>", small_style),
            Paragraph("<b>Role</b>", small_style),
            Paragraph("<b>Failure Handling</b>", small_style),
        ],
        [
            Paragraph("Primary Model", small_style),
            Paragraph(
                "Fast structured extraction",
                small_style,
            ),
            Paragraph(
                "Retry on temporary failure.",
                small_style,
            ),
        ],
        [
            Paragraph("Fallback Model", small_style),
            Paragraph(
                "Alternative extraction path",
                small_style,
            ),
            Paragraph(
                "Used when the primary request fails or output is invalid.",
                small_style,
            ),
        ],
        [
            Paragraph("Safe Default", small_style),
            Paragraph(
                "Protect downstream processing",
                small_style,
            ),
            Paragraph(
                "Used for fields where a safe default is defined.",
                small_style,
            ),
        ],
    ]

    table3 = Table(
        llm_data,
        colWidths=[115, 185, 240],
        repeatRows=1,
    )

    table3.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table3)
    story.append(Spacer(1, 10))

    # 7. Entity Resolution
    story.append(
        Paragraph(
            "7. Entity Resolution Strategy",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Web data frequently contains multiple representations of the same "
            "company. FrontierAtlas uses normalization and fuzzy matching against "
            "a canonical seed list to reduce duplicate entities.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Normalization:</b> lowercasing, whitespace cleanup, punctuation "
            "normalization, and legal suffix handling.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Exact matching:</b> normalized names are first compared directly "
            "against the canonical entity list.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Fuzzy matching:</b> RapidFuzz is used only after normalization "
            "with a configured similarity threshold.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>False-positive protection:</b> the matching strategy avoids "
            "treating a common word such as 'AI' as sufficient evidence that two "
            "companies are the same entity.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Audit trail:</b> raw-to-canonical decisions are retained in "
            "entity_mapping_log.csv.",
            bullet_style,
        )
    )

    # 8. Scale
    story.append(
        Paragraph(
            "8. Scaling Strategy for 500,000+ Records",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "The demo implementation focuses on the required dataset scale, "
            "while the architecture is designed so that ingestion and processing "
            "can be distributed as volume increases.",
            body_style,
        )
    )

    scale_data = [
        [
            Paragraph("<b>Challenge</b>", small_style),
            Paragraph("<b>Current Design</b>", small_style),
            Paragraph("<b>Production Extension</b>", small_style),
        ],
        [
            Paragraph("Large Dataset", small_style),
            Paragraph(
                "Pagination and independent scraper modules",
                small_style,
            ),
            Paragraph(
                "Distributed workers processing independent shards",
                small_style,
            ),
        ],
        [
            Paragraph("Request Concurrency", small_style),
            Paragraph(
                "asyncio + Semaphore",
                small_style,
            ),
            Paragraph(
                "Worker pools with centralized task queue",
                small_style,
            ),
        ],
        [
            Paragraph("Rate Limits", small_style),
            Paragraph(
                "Retry, backoff, jitter, and LLM fallback",
                small_style,
            ),
            Paragraph(
                "Per-provider quotas and adaptive scheduling",
                small_style,
            ),
        ],
        [
            Paragraph("Storage", small_style),
            Paragraph(
                "CSV + Google Sheets",
                small_style,
            ),
            Paragraph(
                "PostgreSQL with batch writes and indexing",
                small_style,
            ),
        ],
    ]

    table4 = Table(
        scale_data,
        colWidths=[105, 190, 245],
        repeatRows=1,
    )

    table4.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(table4)

    story.append(PageBreak())

    # ============================================================
    # PAGE 3
    # ============================================================

    story.append(
        Paragraph(
            "9. Distributed Production Architecture",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "At larger scale, the independent scraper modules can be executed "
            "as distributed jobs. A task queue such as Redis/SQS with worker "
            "orchestration such as Celery or Kubernetes Jobs can distribute "
            "pagination ranges, source categories, or other shards.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "The key principle is to keep ingestion workers as stateless as "
            "possible. Shared state such as processed URLs, checkpoints, and "
            "canonical entities should be stored in centralized infrastructure.",
            body_style,
        )
    )

    # 10. Production storage
    story.append(
        Paragraph(
            "10. Production Storage Strategy",
            heading_style,
        )
    )

    storage_data = [
        [
            Paragraph("<b>Technology</b>", small_style),
            Paragraph("<b>Role</b>", small_style),
            Paragraph("<b>Reason</b>", small_style),
        ],
        [
            Paragraph("PostgreSQL", small_style),
            Paragraph("Primary structured database", small_style),
            Paragraph(
                "Suitable for startups, products, papers, jobs, and news "
                "with indexed relational fields and JSONB where needed.",
                small_style,
            ),
        ],
        [
            Paragraph("Neo4j", small_style),
            Paragraph("Graph relationship layer", small_style),
            Paragraph(
                "Useful for multi-hop relationships such as startup → "
                "founder → product → paper.",
                small_style,
            ),
        ],
        [
            Paragraph("pgvector / Vector DB", small_style),
            Paragraph("Semantic search", small_style),
            Paragraph(
                "Useful for similarity search across paper abstracts, "
                "product descriptions, and startup information.",
                small_style,
            ),
        ],
    ]

    table5 = Table(
        storage_data,
        colWidths=[125, 165, 250],
        repeatRows=1,
    )

    table5.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table5)
    story.append(Spacer(1, 12))

    # 11. Distributed freshness
    story.append(
        Paragraph(
            "11. Distributed Deduplication and Freshness",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "When multiple crawler workers are running, the system needs a "
            "shared mechanism to prevent duplicate processing.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Deterministic key:</b> the normalized source URL can act as "
            "an idempotency key.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Database constraint:</b> production storage can enforce "
            "uniqueness on the source URL or URL hash.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Shared state:</b> Redis or database checkpoints can track "
            "last-seen timestamps and processing status across workers.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Shard ownership:</b> workers can be assigned specific feeds, "
            "source categories, or pagination ranges to reduce duplicate crawling.",
            bullet_style,
        )
    )

    # 12. Future anti-bot architecture
    story.append(
        Paragraph(
            "12. Future High-Volume Web Acquisition",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "For sources that require browser rendering or impose strict "
            "anti-automation controls, a production deployment could introduce "
            "browser-based workers, controlled request scheduling, proxy infrastructure, "
            "and source-specific adapters.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "These components are considered production extensions rather than "
            "requirements of the current demo implementation.",
            body_style,
        )
    )

    # 13. Known limitations
    story.append(
        Paragraph(
            "13. Known Limitations and Trade-offs",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "• The demo was developed within a limited implementation window and "
            "focuses on the required dataset coverage rather than fully processing "
            "500,000 records during the demonstration.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• Public APIs and RSS sources can change, become unavailable, or "
            "return incomplete data. Source-specific adapters are therefore required "
            "for long-term maintenance.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• Entity resolution uses deterministic normalization and fuzzy "
            "matching. Ambiguous entities are safer to leave unmatched than to "
            "force an incorrect canonical mapping.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• CSV and Google Sheets are suitable for demonstration and review, "
            "but a production deployment would require a database with indexing, "
            "constraints, monitoring, and controlled ingestion.",
            bullet_style,
        )
    )

    # 14. Deliverables
    story.append(
        Paragraph(
            "14. Deliverables",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Google Sheets Data Hub:</b> Six-tab structured output containing "
            "startups, products, papers, jobs, news, and entity mappings.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Python Pipeline:</b> Modular scraper, extraction, resolution, "
            "and processing scripts under the src/ directory.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Structured Outputs:</b> CSV datasets under the output/ directory.",
            bullet_style,
        )
    )

    story.append(
        Paragraph(
            "• <b>Architecture Documentation:</b> This PDF describing the current "
            "system and production scaling approach.",
            bullet_style,
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>FrontierAtlas</b> — AI ecosystem data ingestion, extraction, "
            "normalization, and intelligence pipeline.",
            body_style,
        )
    )

    doc.build(story)

    print(f"Successfully generated architecture PDF at: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()