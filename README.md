# Candidate Resume Search Platform

A searchable platform for Millennium Management's BD team to identify and filter analyst talent across geographies, investment strategies, and sectors.

## What it does

- **Parses** PDF and Word resumes using the Anthropic API (Claude Haiku), extracting 20+ structured fields per candidate
- **Stores** parsed data as JSON and CSV for fast, API-free querying
- **Serves** a Streamlit web app where BD users can search and filter candidates across multiple dimensions

## Live App

🔗 [millennium-ds-case-study.streamlit.app](https://millennium-ds-case-study.streamlit.app) *(link updated after deployment)*

## Filters

| Filter | Description |
|---|---|
| Free text search | Searches across all fields — firms, schools, roles, skills |
| Geography | US / Europe / Asia-Pacific |
| Investment strategy | Fundamental Equity, Quantitative/Systematic, Credit, Macro |
| Sector coverage | Healthcare, Technology, Credit, Energy, etc. |
| Seniority | Junior / Mid-level / Senior |
| Years of experience | Range slider |
| Credentials | CFA, MBA, PhD, MSc, FRM |
| Technical skills | Python, R, SQL, C++, Bloomberg, etc. |
| Additional languages | Non-English language filters for cross-border mandates |
| Market side | Buy-side vs. sell-side background |
| Top school | Ivy League, MIT, Stanford, LSE, Oxford, Cambridge, etc. |
| Currently employed | Availability signal |
| Private markets exp. | Relevant for credit / opportunistic pods |

## Project structure

```
├── app.py                                    # Streamlit application
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

Parsing is a one-time ETL step, not a live operation. The app reads from cached JSON — search and filtering runs at millisecond speed with no API calls. This mirrors production architectures where document ingestion is a background pipeline separate from the user-facing search layer.

```
PDF / Word files
      │
      ▼
parse_resumes.py  ──►  candidates.json / candidates.csv
                                │
                                ▼
                          app.py (Streamlit)
                                │
                                ▼
                          BD User Search
```

## Scalability notes

See the notebook (Part 6) for a full discussion. Short version:
- Swap JSON storage → PostgreSQL + pgvector for concurrent access and vector similarity search
- Add async parsing queue (SQS / Celery) to handle bulk uploads without blocking
- Enforce JSON schema via Anthropic tool-use mode to eliminate parsing edge cases
- Cost at scale: ~$2.50 to parse 10,000 resumes with Claude Haiku
