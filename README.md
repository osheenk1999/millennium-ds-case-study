# CORE — Candidate Overview & Recruiting Engine

A searchable candidate platform for Millennium Management's Business Development team. Built as a submission for the 2025 Data Science Case Study.

## Live App

🔗 [millennium-ds-case-study.streamlit.app](https://millennium-ds-case-study.streamlit.app)

## What it does

- **Parses** PDF and Word resumes using the Anthropic API (Claude Haiku), extracting 20+ structured fields per candidate
- **Stores** parsed data as JSON and CSV for fast, API-free querying at runtime
- **Serves** a Streamlit web app where BD users can search, filter, sort, and export candidates across multiple dimensions
- **Surfaces insights** via interactive charts: strategy breakdown, geographic distribution, seniority mix, sector coverage
- **Expands** per-card to show full structured profile — all experience, education, contact details, and skills
- **Recommends** similar candidates per profile, scored by sector/strategy/seniority overlap
- **Flags data quality** — missing contact fields and profile completeness score on every card

## Filters

| Filter | Description |
|---|---|
| Free text search | Searches across all fields — firms, schools, roles, skills, summaries |
| Geography | US / Europe / Asia-Pacific |
| Investment strategy | Fundamental Equity, Quantitative/Systematic, Credit, Macro |
| Sector coverage | Healthcare, Technology, Credit, Energy, Consumer, etc. |
| Seniority | Junior / Mid-level / Senior |
| Years of experience | Range slider |
| Credentials | CFA, MBA, PhD, MSc, FRM |
| Technical skills | Python, R, SQL, C++, Bloomberg, etc. |
| Additional languages | Non-English language filters for cross-border mandates |
| Market side | Buy-side vs. sell-side background |
| Top school | Ivy League, MIT, Stanford, LSE, Oxford, Cambridge, IIT, INSEAD, etc. |
| Currently employed | Availability signal |
| Private markets exp. | Relevant for credit / opportunistic pods |
| Quant skills | Python/R/C++/Matlab — one-click quant filter |

## Sort & export

- Sort by years of experience (high/low), seniority (senior first), or name A→Z
- Export the current filtered view as CSV with one click

## Project structure

```
├── app.py                                    # Streamlit application (CORE)
├── parse_resumes.py                          # LLM parsing script (run once)
├── candidates.json                           # Parsed candidate data (cached)
├── candidates.csv                            # Flat CSV export
├── requirements.txt                          # Python dependencies
└── 2025_ds_case_study_resume_platform.ipynb # Full notebook with code + discussion
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

To re-parse resumes from source files:

```bash
export ANTHROPIC_API_KEY=your_key_here
python parse_resumes.py
```

## Architecture

Parsing is a one-time ETL step, not a live operation. The app reads from cached JSON — all search, filtering, sorting, and similarity scoring runs at millisecond speed with zero API calls at runtime. This mirrors production architectures where document ingestion is a background pipeline separate from the user-facing search layer.

```
PDF / Word files
      │
      ▼
parse_resumes.py  ──►  candidates.json / candidates.csv
                                │
                                ▼
                          app.py (Streamlit / CORE)
                                │
                                ▼
                    Filter · Sort · Export · Expand
```

## Scalability notes

See the notebook (Part 6) for a full discussion. Short version:
- Swap JSON storage → PostgreSQL + pgvector for concurrent access and vector similarity search
- Add async parsing queue (SQS / Celery) to handle bulk uploads without blocking
- Enforce JSON schema via Anthropic tool-use mode to eliminate parsing edge cases
- Embed candidate profiles for semantic search ("find candidates similar to our best healthcare analyst")
- Cost at scale: ~$2.50 to parse 10,000 resumes with Claude Haiku
