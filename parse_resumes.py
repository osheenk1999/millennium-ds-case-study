"""
Resume Parser — Millennium DS Case Study
Extracts structured candidate data from PDF and Word resumes using Claude API.
Results are cached to candidates.json / candidates.csv so the Streamlit app
never needs to make live API calls.
"""

import os
import json
import csv
import re
import subprocess
import requests
import zipfile
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("ANTHROPIC_API_KEY"))
MODEL   = "claude-haiku-4-5"       # fast + cheap for structured extraction
RESUME_DIR = Path("/tmp/claude-0/-home-claude/5b56e0d8-6487-5adc-b7c6-c74ce1c9d2f7/scratchpad/case_study_untrusted")
OUT_JSON = Path("/home/claude/candidates.json")
OUT_CSV  = Path("/home/claude/candidates.csv")

EXTRACTION_PROMPT = """
You are a resume parser for a hedge fund recruiting platform. Extract structured data from the resume text below and return ONLY valid JSON — no explanation, no markdown, no code fences.

Extract these fields exactly:

{
  "name": "Full name",
  "email": "email address or null",
  "phone": "phone number or null",
  "location": "City, Country — infer from phone/address/school if not explicit",
  "geography": "one of: US, Europe, Asia-Pacific, Other",
  "languages": ["list of spoken languages, always include English if it appears"],
  "education": [
    {
      "school": "institution name",
      "degree": "degree type e.g. MBA, BSc, MSc, PhD, CFA",
      "field": "field of study",
      "year_end": 2023
    }
  ],
  "top_school": true,
  "credentials": ["CFA", "MBA", "PhD", "MSc", "FRM", etc — all notable credentials as list],
  "experience": [
    {
      "firm": "company name",
      "role": "job title",
      "start_year": 2020,
      "end_year": 2024,
      "current": false,
      "firm_type": "one of: hedge_fund, asset_manager, investment_bank, private_equity, consulting, corporate, academia, other",
      "aum_approx": "approximate AUM of firm e.g. $40B or null if unknown",
      "sector": ["list of sectors covered e.g. Healthcare, Technology, Energy"],
      "strategy": ["list of strategies e.g. Long/Short Equity, Quant, Macro, Credit, Venture"]
    }
  ],
  "years_experience": 5,
  "seniority": "one of: Student, Junior (0-3 yrs), Mid-level (3-7 yrs), Senior (7+ yrs)",
  "market_type": ["buy_side", "sell_side"] — include all that apply,
  "primary_sectors": ["top 1-3 sectors of expertise"],
  "primary_strategy": "one of: Fundamental Equity, Quantitative/Systematic, Credit, Macro, Multi-Strategy, Other",
  "public_markets": true,
  "private_markets": false,
  "technical_skills": ["Python", "R", "SQL", "C++", "Excel", "Bloomberg" — any mentioned],
  "currently_employed": true,
  "notable_firms": ["any well-known firms e.g. Goldman Sachs, Citadel, Two Sigma"],
  "summary": "2-3 sentence professional summary you write based on their background"
}

Rules:
- top_school = true if any of: Ivy League, MIT, Stanford, LSE, Oxford, Cambridge, IIT, HKU, INSEAD, Wharton, Chicago Booth, Michigan Ross, MIT Sloan, HBS
- years_experience = current year (2025) minus first full-time job year
- currently_employed = true if most recent role has no end date / says "present"
- For sectors/strategies, be specific — "Healthcare" not "Finance"
- If a field is truly unknown, use null

Resume text:
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_pdf(path: Path) -> str:
    """Extract text from PDF using pdftotext."""
    result = subprocess.run(
        ["pdftotext", str(path), "-"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def extract_text_docx(path: Path) -> str:
    """Extract text from Word document."""
    import zipfile
    import xml.etree.ElementTree as ET

    text_parts = []
    with zipfile.ZipFile(path, "r") as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            for para in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                runs = para.findall(".//w:t", ns)
                line = "".join(r.text or "" for r in runs)
                if line.strip():
                    text_parts.append(line.strip())
    return "\n".join(text_parts)


def call_claude(text: str) -> dict:
    """Send resume text to Claude and return parsed JSON."""
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": MODEL,
            "max_tokens": 1500,
            "messages": [
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT + text[:8000]  # token cap
                }
            ]
        },
        timeout=30
    )
    response.raise_for_status()
    raw = response.json()["content"][0]["text"].strip()

    # Strip markdown code fences if model added them
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    return json.loads(raw)


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_all_resumes():
    candidates = []
    files = list(RESUME_DIR.glob("*.pdf")) + list(RESUME_DIR.glob("*.docx"))
    files = sorted(files)

    for i, path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Parsing: {path.name}")
        try:
            if path.suffix == ".pdf":
                text = extract_text_pdf(path)
            else:
                text = extract_text_docx(path)

            if not text.strip():
                print(f"  ⚠ No text extracted from {path.name}, skipping")
                continue

            data = call_claude(text)
            data["source_file"] = path.name
            data["parsed_at"] = datetime.now().isoformat()
            candidates.append(data)
            print(f"  ✓ {data.get('name', 'Unknown')}")

        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parse error for {path.name}: {e}")
        except Exception as e:
            print(f"  ✗ Error for {path.name}: {e}")

    # Save JSON
    OUT_JSON.write_text(json.dumps(candidates, indent=2))
    print(f"\n✓ Saved {len(candidates)} candidates to {OUT_JSON}")

    # Save CSV (flatten key fields)
    if candidates:
        flat_fields = [
            "name", "email", "location", "geography", "years_experience",
            "seniority", "primary_strategy", "currently_employed",
            "top_school", "public_markets", "private_markets", "source_file"
        ]
        list_fields = [
            "languages", "credentials", "primary_sectors",
            "technical_skills", "notable_firms", "market_type"
        ]
        with OUT_CSV.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=flat_fields + list_fields)
            writer.writeheader()
            for c in candidates:
                row = {k: c.get(k, "") for k in flat_fields}
                for lf in list_fields:
                    val = c.get(lf, [])
                    row[lf] = ", ".join(val) if isinstance(val, list) else str(val)
                writer.writerow(row)
        print(f"✓ Saved CSV to {OUT_CSV}")

    return candidates


if __name__ == "__main__":
    parse_all_resumes()
