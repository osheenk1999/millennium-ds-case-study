"""
CORE — Candidate Overview & Recruiting Engine
Millennium Management · Business Development
"""

import json
import html
from pathlib import Path

import streamlit as st
import plotly.express as px

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CORE · Candidate Overview & Recruiting Engine",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background: #f4f6fa;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0c1a2e;
    }
    /* All sidebar text white */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #e0e8f4 !important;
    }
    /* Filter labels */
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stCheckbox label,
    [data-testid="stSidebar"] .stTextInput label {
        color: #7a9cc4 !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
    /* Sidebar input fields — visible text */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] .stTextInput input {
        color: #0c1a2e !important;
        background: #ffffff !important;
        border: 1.5px solid #2e5080 !important;
        border-radius: 6px !important;
    }
    /* Multiselect chips */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #1e3a5f !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: #aecdee !important;
    }
    /* Multiselect dropdown text */
    [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #0c1a2e !important;
    }
    [data-testid="stSidebar"] [data-baseweb="popover"] * {
        color: #0c1a2e !important;
    }
    /* Divider */
    [data-testid="stSidebar"] hr {
        border-color: #1e3358 !important;
    }

    /* ── Cards ── */
    .c-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 1.2rem 1.4rem 1rem 1.4rem;
        margin-bottom: 0.65rem;
        border: 1px solid #dde4ef;
    }
    .c-name {
        font-size: 1rem;
        font-weight: 700;
        color: #0c1a2e;
        margin: 0 0 0.15rem 0;
        line-height: 1.3;
    }
    .c-role {
        font-size: 0.8rem;
        color: #4a6080;
        margin: 0 0 0.7rem 0;
    }
    .tag {
        display: inline-block;
        border-radius: 4px;
        padding: 0.12rem 0.5rem;
        font-size: 0.68rem;
        font-weight: 600;
        margin: 0.1rem 0.15rem 0.1rem 0;
        letter-spacing: 0.02em;
    }
    .tag-default { background:#edf1fb; color:#2a4a8a; }
    .tag-green   { background:#e6f4ec; color:#1a6b38; }
    .tag-amber   { background:#fdf3e0; color:#7a5000; }
    .tag-red     { background:#fdecea; color:#8b1a1a; }
    .c-summary {
        font-size: 0.8rem;
        color: #4a6080;
        margin: 0.5rem 0 0.55rem 0;
        line-height: 1.55;
    }
    .c-meta {
        font-size: 0.72rem;
        color: #8096b4;
        border-top: 1px solid #edf0f6;
        padding-top: 0.5rem;
        margin-top: 0.1rem;
    }
    .c-meta strong { color: #3a5a8a; }

    /* ── Metrics ── */
    .metric-row {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
    }
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        flex: 1;
        border: 1px solid #dde4ef;
        text-align: center;
    }
    .metric-val   { font-size: 1.7rem; font-weight: 800; color: #0c1a2e; line-height: 1; }
    .metric-lbl   { font-size: 0.65rem; color: #8096b4; text-transform: uppercase;
                    letter-spacing: 0.07em; margin-top: 0.25rem; font-weight: 600; }

    /* ── Page title ── */
    .page-title    { font-size: 1.5rem; font-weight: 800; color: #0c1a2e; margin:0; letter-spacing:-0.02em; }
    .page-sub      { font-size: 0.8rem; color: #8096b4; margin: 0.15rem 0 1.2rem 0; }

    /* ── Misc ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────

@st.cache_data
def load_candidates():
    path = Path(__file__).parent / "candidates.json"
    with open(path) as f:
        raw = json.load(f)
    records = []
    for c in raw:
        records.append({
            "name":               c.get("name", "Unknown"),
            "email":              c.get("email") or "",
            "location":           c.get("location") or "",
            "geography":          c.get("geography", "Other"),
            "languages":          c.get("languages", []),
            "credentials":        c.get("credentials", []),
            "years_experience":   int(c.get("years_experience") or 0),
            "seniority":          c.get("seniority", "Unknown"),
            "primary_strategy":   c.get("primary_strategy", "Other"),
            "market_type":        c.get("market_type", []),
            "primary_sectors":    c.get("primary_sectors", []),
            "technical_skills":   c.get("technical_skills", []),
            "currently_employed": bool(c.get("currently_employed", True)),
            "top_school":         bool(c.get("top_school", False)),
            "public_markets":     bool(c.get("public_markets", True)),
            "private_markets":    bool(c.get("private_markets", False)),
            "notable_firms":      c.get("notable_firms", []),
            "education":          c.get("education", []),
            "experience":         c.get("experience", []),
            "summary":            c.get("summary", ""),
            "source_file":        c.get("source_file", ""),
        })
    return records


def list_vals(candidates, field):
    vals = set()
    for c in candidates:
        for v in c.get(field, []):
            if v:
                vals.add(v)
    return sorted(vals)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(candidates):
    with st.sidebar:
        st.markdown("""
        <div style="padding:1rem 0 1.4rem 0; border-bottom:1px solid #1e3358; margin-bottom:1.3rem;">
            <div style="font-size:1.15rem; font-weight:800; color:#ffffff; letter-spacing:-0.01em;">CORE</div>
            <div style="font-size:0.72rem; color:#5a7a9e; margin-top:0.15rem;">Candidate Overview &amp; Recruiting Engine</div>
        </div>
        """, unsafe_allow_html=True)

        search_query = st.text_input("Search candidates", placeholder="Goldman, Python, healthcare...")

        st.divider()

        geography = st.multiselect("Geography", sorted(set(c["geography"] for c in candidates)))
        strategy  = st.multiselect("Investment Strategy", sorted(set(c["primary_strategy"] for c in candidates)))
        sectors   = st.multiselect("Sector Coverage", list_vals(candidates, "primary_sectors"))
        seniority = st.multiselect("Seniority", ["Junior (0-3 yrs)", "Mid-level (3-7 yrs)", "Senior (7+ yrs)"])

        st.divider()

        years_range  = st.slider("Years of Experience", 0, 20, (0, 20))
        credentials  = st.multiselect("Credentials", list_vals(candidates, "credentials"))
        skills       = st.multiselect("Technical Skills", list_vals(candidates, "technical_skills"))
        extra_langs  = [l for l in list_vals(candidates, "languages") if l.lower() != "english"]
        languages    = st.multiselect("Additional Languages", extra_langs)

        st.divider()

        market_type = st.multiselect(
            "Market Side", ["buy_side", "sell_side"],
            format_func=lambda x: "Buy-side" if x == "buy_side" else "Sell-side"
        )
        col1, col2 = st.columns(2)
        top_school_only    = col1.checkbox("Top School")
        currently_employed = col2.checkbox("Employed")
        private_markets    = st.checkbox("Private Markets Exp.")
        quant_only         = st.checkbox("Quant Skills (Python/R/C++)")

    return dict(
        search_query=search_query, geography=geography, strategy=strategy,
        sectors=sectors, seniority=seniority, years_range=years_range,
        credentials=credentials, skills=skills, languages=languages,
        market_type=market_type, top_school_only=top_school_only,
        currently_employed=currently_employed, private_markets=private_markets,
        quant_only=quant_only,
    )


# ── Filtering ─────────────────────────────────────────────────────────────────

def apply_filters(candidates, f):
    quant = {"python", "r", "c++", "matlab", "julia", "sql"}
    out = []
    for c in candidates:
        q = f["search_query"].lower().strip()
        if q:
            blob = " ".join([
                c["name"], c["location"], c["summary"],
                " ".join(c["credentials"]), " ".join(c["primary_sectors"]),
                " ".join(c["technical_skills"]), " ".join(c["notable_firms"]),
                " ".join(c["languages"]),
                " ".join(e.get("firm","")+" "+e.get("role","") for e in c["experience"]),
                " ".join(e.get("school","")+" "+e.get("field","") for e in c["education"]),
            ]).lower()
            if q not in blob:
                continue
        if f["geography"]   and c["geography"] not in f["geography"]: continue
        if f["strategy"]    and c["primary_strategy"] not in f["strategy"]: continue
        if f["sectors"]     and not any(s in c["primary_sectors"] for s in f["sectors"]): continue
        if f["seniority"]   and c["seniority"] not in f["seniority"]: continue
        if not (f["years_range"][0] <= c["years_experience"] <= f["years_range"][1]): continue
        if f["credentials"] and not any(cr in c["credentials"] for cr in f["credentials"]): continue
        if f["skills"]      and not any(sk in c["technical_skills"] for sk in f["skills"]): continue
        if f["languages"]   and not any(lg in c["languages"] for lg in f["languages"]): continue
        if f["market_type"] and not any(mt in c["market_type"] for mt in f["market_type"]): continue
        if f["top_school_only"]    and not c["top_school"]: continue
        if f["currently_employed"] and not c["currently_employed"]: continue
        if f["private_markets"]    and not c["private_markets"]: continue
        if f["quant_only"] and not {s.lower() for s in c["technical_skills"]} & quant: continue
        out.append(c)
    return out


# ── Candidate card ────────────────────────────────────────────────────────────

def tag(text, cls="tag-default"):
    t = html.escape(str(text))
    return f'<span class="tag {cls}">{t}</span>'


def render_card(c):
    # Safely escape all user content
    name     = html.escape(c["name"])
    location = html.escape(c["location"])
    summary  = html.escape(c["summary"])

    # Current role
    current_role = ""
    for exp in c["experience"]:
        if exp.get("current"):
            current_role = html.escape(f'{exp.get("role","")} @ {exp.get("firm","")}')
            break
    if not current_role and c["experience"]:
        exp = c["experience"][0]
        current_role = html.escape(f'{exp.get("role","")} @ {exp.get("firm","")}')

    role_line = current_role
    if location:
        role_line = f"{current_role} &nbsp;·&nbsp; {location}" if current_role else location

    # Tags row
    tags_html = ""
    tags_html += tag(c["geography"])
    tags_html += tag(c["primary_strategy"], "tag-amber")
    tags_html += tag(c["seniority"])
    for cr in c["credentials"][:3]:
        tags_html += tag(cr, "tag-green")
    for s in c["primary_sectors"][:3]:
        tags_html += tag(s)

    # Status badges (top-right)
    badges = ""
    if c["currently_employed"]:
        badges += tag("Employed", "tag-green")
    else:
        badges += tag("Available", "tag-red")
    if c["top_school"]:
        badges += tag("Top School", "tag-green")

    # Meta row
    skills_str = html.escape(", ".join(c["technical_skills"][:5]) or "—")
    extra_langs = [l for l in c["languages"] if l.lower() != "english"]
    lang_str = html.escape(", ".join(extra_langs[:3]))
    yrs = c["years_experience"]

    meta_parts = [f"<strong>Skills:</strong> {skills_str}"]
    if lang_str:
        meta_parts.append(f"<strong>Languages:</strong> {lang_str}")
    meta_parts.append(f"<strong>Experience:</strong> {yrs} yrs")
    meta_html = " &nbsp;·&nbsp; ".join(meta_parts)

    st.markdown(f"""
<div class="c-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
    <div style="min-width:0;">
      <div class="c-name">{name}</div>
      <div class="c-role">{role_line}</div>
    </div>
    <div style="flex-shrink:0;">{badges}</div>
  </div>
  <div style="margin-bottom:0.4rem;">{tags_html}</div>
  <div class="c-summary">{summary}</div>
  <div class="c-meta">{meta_html}</div>
</div>
""", unsafe_allow_html=True)


# ── Charts ────────────────────────────────────────────────────────────────────

BLUES = ["#0c3060", "#1a5090", "#2e74bc", "#5b9bd5", "#8fbce8", "#c2daf5"]

CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#2a3a50", size=11),
    margin=dict(t=45, b=10, l=10, r=10),
    height=290,
)


def render_charts(filtered):
    col1, col2 = st.columns(2)

    with col1:
        counts = {}
        for c in filtered:
            counts[c["primary_strategy"]] = counts.get(c["primary_strategy"], 0) + 1
        fig = px.bar(
            x=list(counts.keys()), y=list(counts.values()),
            title="Strategy Breakdown",
            labels={"x": "Strategy", "y": "# Candidates"},
            color_discrete_sequence=["#2e74bc"],
        )
        fig.update_layout(**CHART_LAYOUT, showlegend=False)
        fig.update_xaxes(title_text="Strategy", tickfont_size=9)
        fig.update_yaxes(title_text="Candidates", tickfont_size=10, dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        geos = {}
        for c in filtered:
            geos[c["geography"]] = geos.get(c["geography"], 0) + 1
        fig2 = px.pie(
            names=list(geos.keys()), values=list(geos.values()),
            title="Geographic Distribution",
            color_discrete_sequence=BLUES, hole=0.42,
        )
        fig2.update_layout(**CHART_LAYOUT, legend=dict(font_size=10))
        fig2.update_traces(textfont_size=10, textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        sen_order = ["Junior (0-3 yrs)", "Mid-level (3-7 yrs)", "Senior (7+ yrs)"]
        labels    = ["Junior", "Mid-level", "Senior"]
        vals      = [sum(1 for c in filtered if c["seniority"] == s) for s in sen_order]
        fig3 = px.bar(
            x=labels, y=vals,
            title="Seniority Mix",
            labels={"x": "Level", "y": "# Candidates"},
            color_discrete_sequence=["#0c3060"],
        )
        fig3.update_layout(**CHART_LAYOUT, showlegend=False)
        fig3.update_xaxes(title_text="Seniority Level")
        fig3.update_yaxes(title_text="Candidates", dtick=1)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        sector_counts = {}
        for c in filtered:
            for s in c["primary_sectors"]:
                sector_counts[s] = sector_counts.get(s, 0) + 1
        top = sorted(sector_counts.items(), key=lambda x: -x[1])[:8]
        if top:
            fig4 = px.bar(
                x=[v for _, v in top], y=[s for s, _ in top],
                orientation="h",
                title="Sector Coverage",
                labels={"x": "# Candidates", "y": "Sector"},
                color_discrete_sequence=["#5b9bd5"],
            )
            fig4.update_layout(**CHART_LAYOUT, showlegend=False)
            fig4.update_xaxes(title_text="Candidates", dtick=1)
            fig4.update_yaxes(title_text="", tickfont_size=9)
            st.plotly_chart(fig4, use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    candidates = load_candidates()
    filters    = render_sidebar(candidates)
    filtered   = apply_filters(candidates, filters)

    # Header
    col_t, col_n = st.columns([3, 1])
    with col_t:
        st.markdown('<div class="page-title">CORE</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Candidate Overview &amp; Recruiting Engine &nbsp;·&nbsp; Millennium Management BD &nbsp;·&nbsp; <span style="color:#b0c4de;">10 candidates · demo dataset</span></div>', unsafe_allow_html=True)
    with col_n:
        st.markdown(f"""
        <div style="text-align:right;padding-top:0.4rem;">
          <span style="font-size:1.9rem;font-weight:800;color:#0c1a2e;">{len(filtered)}</span>
          <span style="font-size:0.75rem;color:#8096b4;display:block;">of {len(candidates)} candidates</span>
        </div>""", unsafe_allow_html=True)

    # Metric strip
    employed  = sum(1 for c in filtered if c["currently_employed"])
    buy_side  = sum(1 for c in filtered if "buy_side" in c.get("market_type", []))
    top_sch   = sum(1 for c in filtered if c["top_school"])
    avg_exp   = round(sum(c["years_experience"] for c in filtered) / max(len(filtered), 1), 1)

    st.markdown(f"""
<div class="metric-row">
  <div class="metric-card"><div class="metric-val">{len(filtered)}</div><div class="metric-lbl">Matching</div></div>
  <div class="metric-card"><div class="metric-val">{employed}</div><div class="metric-lbl">Employed</div></div>
  <div class="metric-card"><div class="metric-val">{buy_side}</div><div class="metric-lbl">Buy-Side</div></div>
  <div class="metric-card"><div class="metric-val">{top_sch}</div><div class="metric-lbl">Top School</div></div>
  <div class="metric-card"><div class="metric-val">{avg_exp}</div><div class="metric-lbl">Avg. Yrs Exp.</div></div>
</div>""", unsafe_allow_html=True)

    # Sort + export bar
    col_sort, col_exp = st.columns([3, 1])
    with col_sort:
        sort_by = st.selectbox(
            "Sort by",
            ["Years Experience (high → low)", "Years Experience (low → high)",
             "Seniority (senior first)", "Name (A → Z)"],
            label_visibility="collapsed",
        )
    with col_exp:
        if filtered:
            import io
            import csv as _csv
            buf = io.StringIO()
            flat = ["name","location","geography","seniority","years_experience",
                    "primary_strategy","currently_employed","top_school","market_type",
                    "primary_sectors","credentials","technical_skills","notable_firms","summary"]
            w = _csv.DictWriter(buf, fieldnames=flat)
            w.writeheader()
            for c in filtered:
                row = {k: (", ".join(c[k]) if isinstance(c[k], list) else c[k]) for k in flat}
                w.writerow(row)
            st.download_button(
                "⬇ Export CSV",
                data=buf.getvalue(),
                file_name="core_candidates_filtered.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # Sort
    seniority_order = {"Junior (0-3 yrs)": 0, "Mid-level (3-7 yrs)": 1, "Senior (7+ yrs)": 2}
    if sort_by == "Years Experience (high → low)":
        filtered = sorted(filtered, key=lambda c: c["years_experience"], reverse=True)
    elif sort_by == "Years Experience (low → high)":
        filtered = sorted(filtered, key=lambda c: c["years_experience"])
    elif sort_by == "Seniority (senior first)":
        filtered = sorted(filtered, key=lambda c: seniority_order.get(c["seniority"], 0), reverse=True)
    else:
        filtered = sorted(filtered, key=lambda c: c["name"])

    # Tabs
    tab1, tab2 = st.tabs([f"Results ({len(filtered)})", "Insights (filtered)"])

    with tab1:
        if not filtered:
            st.info("No candidates match the current filters.")
        else:
            for c in filtered:
                render_card(c)

    with tab2:
        if not filtered:
            st.info("No candidates to display.")
        else:
            render_charts(filtered)


if __name__ == "__main__":
    main()
