"""
Candidate Resume Search Platform — Millennium Management
Built for the BD team to quickly identify analyst talent across
geographies, strategies, and sectors.
"""

import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Candidate Search — Millennium BD",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    [data-testid="stAppViewContainer"] {
        background: #f7f8fa;
    }
    [data-testid="stSidebar"] {
        background: #0a1628;
    }
    [data-testid="stSidebar"] * {
        color: #e8edf5 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #9aafc8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }
    /* Sidebar header */
    .sidebar-header {
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid #1e3a5f;
        margin-bottom: 1.5rem;
    }
    .sidebar-header h2 {
        color: #ffffff !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.02em;
    }
    .sidebar-header p {
        color: #6b8cae !important;
        font-size: 0.75rem;
        margin: 0.25rem 0 0 0;
    }
    /* Candidate card */
    .candidate-card {
        background: white;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
        border: 1px solid #e5e9f0;
        transition: box-shadow 0.15s ease;
    }
    .candidate-card:hover {
        box-shadow: 0 4px 16px rgba(10, 22, 40, 0.08);
    }
    .candidate-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0a1628;
        margin: 0 0 0.2rem 0;
    }
    .candidate-title {
        font-size: 0.82rem;
        color: #4a6080;
        margin: 0 0 0.75rem 0;
    }
    .tag {
        display: inline-block;
        background: #eef2f9;
        color: #2a4a7a;
        border-radius: 4px;
        padding: 0.15rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 600;
        margin: 0.1rem 0.2rem 0.1rem 0;
        letter-spacing: 0.02em;
    }
    .tag-green {
        background: #eaf5ee;
        color: #1a6b35;
    }
    .tag-amber {
        background: #fdf4e3;
        color: #7a5200;
    }
    .tag-red {
        background: #fdecea;
        color: #8b1a1a;
    }
    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        flex: 1;
        border: 1px solid #e5e9f0;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0a1628;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.72rem;
        color: #6b8cae;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.3rem;
        font-weight: 600;
    }
    /* Section header */
    .section-header {
        font-size: 0.7rem;
        font-weight: 700;
        color: #9aafc8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 0.5rem 0;
    }
    /* Page title */
    .page-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0a1628;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .page-subtitle {
        font-size: 0.85rem;
        color: #6b8cae;
        margin: 0.2rem 0 1.5rem 0;
    }
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Search box */
    [data-testid="stTextInput"] input {
        border-radius: 8px !important;
        border: 1.5px solid #d0d9e8 !important;
        font-size: 0.9rem !important;
    }
    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly .bg {
        fill: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_candidates():
    data_path = Path(__file__).parent / "candidates.json"
    with open(data_path) as f:
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
            "years_experience":   c.get("years_experience", 0) or 0,
            "seniority":          c.get("seniority", "Unknown"),
            "primary_strategy":   c.get("primary_strategy", "Other"),
            "market_type":        c.get("market_type", []),
            "primary_sectors":    c.get("primary_sectors", []),
            "technical_skills":   c.get("technical_skills", []),
            "currently_employed": c.get("currently_employed", True),
            "top_school":         c.get("top_school", False),
            "public_markets":     c.get("public_markets", True),
            "private_markets":    c.get("private_markets", False),
            "notable_firms":      c.get("notable_firms", []),
            "education":          c.get("education", []),
            "experience":         c.get("experience", []),
            "summary":            c.get("summary", ""),
            "source_file":        c.get("source_file", ""),
        })
    return records


def list_field_values(candidates, field):
    """Get all unique values from a list field."""
    vals = set()
    for c in candidates:
        for v in c.get(field, []):
            if v:
                vals.add(v)
    return sorted(vals)


def matches_text_search(candidate, query: str) -> bool:
    """Full-text search across all candidate fields."""
    if not query.strip():
        return True
    query = query.lower()
    searchable = " ".join([
        candidate.get("name", ""),
        candidate.get("location", ""),
        candidate.get("summary", ""),
        " ".join(candidate.get("credentials", [])),
        " ".join(candidate.get("primary_sectors", [])),
        " ".join(candidate.get("technical_skills", [])),
        " ".join(candidate.get("notable_firms", [])),
        " ".join(candidate.get("languages", [])),
        " ".join([e.get("firm", "") + " " + e.get("role", "") for e in candidate.get("experience", [])]),
        " ".join([e.get("school", "") + " " + e.get("field", "") for e in candidate.get("education", [])]),
    ]).lower()
    return query in searchable


# ── Sidebar filters ───────────────────────────────────────────────────────────

def render_sidebar(candidates):
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>🔍 Candidate Search</h2>
            <p>Millennium Management · BD Platform</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-header">Free Text Search</p>', unsafe_allow_html=True)
        search_query = st.text_input(
            "Search",
            placeholder="e.g. Goldman, Python, healthcare...",
            label_visibility="collapsed"
        )

        st.divider()

        all_geos = sorted(set(c["geography"] for c in candidates))
        geography = st.multiselect("Geography", all_geos)

        all_strategies = sorted(set(c["primary_strategy"] for c in candidates))
        strategy = st.multiselect("Investment Strategy", all_strategies)

        all_sectors = list_field_values(candidates, "primary_sectors")
        sectors = st.multiselect("Sector Coverage", all_sectors)

        all_seniority = ["Junior (0-3 yrs)", "Mid-level (3-7 yrs)", "Senior (7+ yrs)"]
        seniority = st.multiselect("Seniority", all_seniority)

        st.divider()

        years_range = st.slider("Years of Experience", 0, 20, (0, 20))

        all_credentials = list_field_values(candidates, "credentials")
        credentials = st.multiselect("Credentials", all_credentials)

        all_skills = list_field_values(candidates, "technical_skills")
        skills = st.multiselect("Technical Skills", all_skills)

        all_langs = list_field_values(candidates, "languages")
        # Remove English — everyone has it, not a useful filter
        all_langs = [l for l in all_langs if l.lower() != "english"]
        languages = st.multiselect("Additional Languages", all_langs)

        st.divider()

        market_type = st.multiselect("Market Side", ["buy_side", "sell_side"],
                                     format_func=lambda x: "Buy-side" if x == "buy_side" else "Sell-side")

        col1, col2 = st.columns(2)
        with col1:
            top_school_only = st.checkbox("Top School")
        with col2:
            currently_employed = st.checkbox("Employed Now")

        private_markets = st.checkbox("Private Markets Exp.")
        quant_only = st.checkbox("Quant Skills (Python/R/C++)")

    return {
        "search_query": search_query,
        "geography": geography,
        "strategy": strategy,
        "sectors": sectors,
        "seniority": seniority,
        "years_range": years_range,
        "credentials": credentials,
        "skills": skills,
        "languages": languages,
        "market_type": market_type,
        "top_school_only": top_school_only,
        "currently_employed": currently_employed,
        "private_markets": private_markets,
        "quant_only": quant_only,
    }


# ── Filter logic ──────────────────────────────────────────────────────────────

def apply_filters(candidates, filters):
    results = []
    quant_skills = {"python", "r", "c++", "matlab", "julia", "sql"}

    for c in candidates:
        if not matches_text_search(c, filters["search_query"]):
            continue
        if filters["geography"] and c["geography"] not in filters["geography"]:
            continue
        if filters["strategy"] and c["primary_strategy"] not in filters["strategy"]:
            continue
        if filters["sectors"]:
            if not any(s in c["primary_sectors"] for s in filters["sectors"]):
                continue
        if filters["seniority"] and c["seniority"] not in filters["seniority"]:
            continue
        yrs = c["years_experience"]
        if not (filters["years_range"][0] <= yrs <= filters["years_range"][1]):
            continue
        if filters["credentials"]:
            if not any(cr in c["credentials"] for cr in filters["credentials"]):
                continue
        if filters["skills"]:
            if not any(sk in c["technical_skills"] for sk in filters["skills"]):
                continue
        if filters["languages"]:
            if not any(lg in c["languages"] for lg in filters["languages"]):
                continue
        if filters["market_type"]:
            if not any(mt in c["market_type"] for mt in filters["market_type"]):
                continue
        if filters["top_school_only"] and not c["top_school"]:
            continue
        if filters["currently_employed"] and not c["currently_employed"]:
            continue
        if filters["private_markets"] and not c["private_markets"]:
            continue
        if filters["quant_only"]:
            cand_skills = {s.lower() for s in c["technical_skills"]}
            if not cand_skills.intersection(quant_skills):
                continue

        results.append(c)

    return results


# ── Candidate card ────────────────────────────────────────────────────────────

def render_candidate_card(c):
    # Build credential tags
    cred_tags = ""
    for cr in c["credentials"][:4]:
        cred_tags += f'<span class="tag tag-green">{cr}</span>'

    # Geography + seniority tags
    geo_tag = f'<span class="tag">{c["geography"]}</span>'
    sen_tag = f'<span class="tag">{c["seniority"]}</span>'
    strat_tag = f'<span class="tag tag-amber">{c["primary_strategy"]}</span>'

    # Sector tags
    sector_tags = ""
    for s in c["primary_sectors"][:3]:
        sector_tags += f'<span class="tag">{s}</span>'

    # Employment status
    employed_tag = (
        '<span class="tag tag-green">Currently Employed</span>'
        if c["currently_employed"]
        else '<span class="tag tag-red">Available</span>'
    )

    # Top school badge
    school_tag = '<span class="tag tag-green">Top School</span>' if c["top_school"] else ""

    # Current role
    current_role = ""
    for exp in c["experience"]:
        if exp.get("current"):
            current_role = f'{exp.get("role", "")} @ {exp.get("firm", "")}'
            break
    if not current_role and c["experience"]:
        exp = c["experience"][0]
        current_role = f'{exp.get("role", "")} @ {exp.get("firm", "")}'

    # Skills
    skills_preview = ", ".join(c["technical_skills"][:5]) if c["technical_skills"] else "—"

    # Languages (beyond English)
    extra_langs = [l for l in c.get("languages", []) if l.lower() != "english"]
    lang_str = ", ".join(extra_langs[:3]) if extra_langs else ""

    # Location
    location = c.get("location", "") or ""

    st.markdown(f"""
    <div class="candidate-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <p class="candidate-name">{c['name']}</p>
                <p class="candidate-title">{current_role} &nbsp;·&nbsp; {location}</p>
            </div>
            <div style="text-align:right;">
                {employed_tag}
                {school_tag}
            </div>
        </div>
        <div style="margin-bottom:0.6rem;">
            {geo_tag}{strat_tag}{sen_tag}{cred_tags}{sector_tags}
        </div>
        <p style="font-size:0.82rem; color:#4a6080; margin:0 0 0.5rem 0; line-height:1.5;">
            {c.get('summary', '')}
        </p>
        <div style="display:flex; gap:2rem; font-size:0.75rem; color:#6b8cae;">
            <span><strong style="color:#2a4a7a;">Skills:</strong> {skills_preview}</span>
            {'<span><strong style="color:#2a4a7a;">Languages:</strong> ' + lang_str + '</span>' if lang_str else ''}
            <span><strong style="color:#2a4a7a;">Experience:</strong> {c['years_experience']} yrs</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Visualizations ────────────────────────────────────────────────────────────

CHART_COLORS = ["#1a3a6b", "#2e6db4", "#5b9bd5", "#8fbce8", "#c2daf5", "#e8f1fb"]

def render_charts(filtered, all_candidates):
    st.markdown("---")
    st.markdown("### Candidate Insights")
    col1, col2 = st.columns(2)

    with col1:
        # Strategy breakdown
        strategies = {}
        for c in filtered:
            s = c["primary_strategy"]
            strategies[s] = strategies.get(s, 0) + 1
        fig = px.bar(
            x=list(strategies.keys()),
            y=list(strategies.values()),
            labels={"x": "", "y": "Candidates"},
            title="By Strategy",
            color_discrete_sequence=["#2e6db4"]
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0a1628", showlegend=False,
            title_font_size=13, margin=dict(t=40, b=20, l=20, r=20),
            height=280
        )
        fig.update_xaxes(tickfont_size=10)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Geography pie
        geos = {}
        for c in filtered:
            g = c["geography"]
            geos[g] = geos.get(g, 0) + 1
        fig2 = px.pie(
            names=list(geos.keys()),
            values=list(geos.values()),
            title="By Geography",
            color_discrete_sequence=CHART_COLORS,
            hole=0.4
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0a1628",
            title_font_size=13, margin=dict(t=40, b=20, l=20, r=20),
            height=280,
            legend=dict(font_size=10)
        )
        fig2.update_traces(textfont_size=10)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Seniority breakdown
        sen_order = ["Junior (0-3 yrs)", "Mid-level (3-7 yrs)", "Senior (7+ yrs)"]
        sen_counts = {s: 0 for s in sen_order}
        for c in filtered:
            sen = c["seniority"]
            if sen in sen_counts:
                sen_counts[sen] += 1
        fig3 = px.bar(
            x=[s.split(" (")[0] for s in sen_order],
            y=[sen_counts[s] for s in sen_order],
            title="By Seniority",
            color_discrete_sequence=["#1a3a6b"]
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0a1628", showlegend=False,
            title_font_size=13, margin=dict(t=40, b=20, l=20, r=20),
            height=260
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Top sectors
        sector_counts = {}
        for c in filtered:
            for s in c["primary_sectors"]:
                sector_counts[s] = sector_counts.get(s, 0) + 1
        sorted_sectors = sorted(sector_counts.items(), key=lambda x: -x[1])[:8]
        if sorted_sectors:
            fig4 = px.bar(
                x=[s[1] for s in sorted_sectors],
                y=[s[0] for s in sorted_sectors],
                orientation="h",
                title="Top Sectors",
                color_discrete_sequence=["#5b9bd5"]
            )
            fig4.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#0a1628", showlegend=False,
                title_font_size=13, margin=dict(t=40, b=20, l=0, r=20),
                height=260
            )
            fig4.update_yaxes(tickfont_size=9)
            st.plotly_chart(fig4, use_container_width=True)


# ── Main app ──────────────────────────────────────────────────────────────────

def main():
    candidates = load_candidates()
    filters = render_sidebar(candidates)
    filtered = apply_filters(candidates, filters)

    # Header
    col_title, col_count = st.columns([3, 1])
    with col_title:
        st.markdown('<p class="page-title">Candidate Pipeline</p>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Millennium Management · Business Development</p>', unsafe_allow_html=True)
    with col_count:
        st.markdown(f"""
        <div style="text-align:right; padding-top:0.5rem;">
            <span style="font-size:2rem; font-weight:800; color:#0a1628;">{len(filtered)}</span>
            <span style="font-size:0.8rem; color:#6b8cae; display:block;">of {len(candidates)} candidates</span>
        </div>
        """, unsafe_allow_html=True)

    # Summary metric row
    employed = sum(1 for c in filtered if c["currently_employed"])
    top_school = sum(1 for c in filtered if c["top_school"])
    buy_side = sum(1 for c in filtered if "buy_side" in c.get("market_type", []))
    avg_exp = round(sum(c["years_experience"] for c in filtered) / max(len(filtered), 1), 1)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-value">{len(filtered)}</div>
            <div class="metric-label">Matching</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{employed}</div>
            <div class="metric-label">Employed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{buy_side}</div>
            <div class="metric-label">Buy-Side</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{top_school}</div>
            <div class="metric-label">Top School</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{avg_exp}</div>
            <div class="metric-label">Avg. Yrs Exp.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs: Results | Insights
    tab1, tab2 = st.tabs([f"Results ({len(filtered)})", "Insights"])

    with tab1:
        if not filtered:
            st.info("No candidates match the current filters. Try broadening your search.")
        else:
            for c in filtered:
                render_candidate_card(c)

    with tab2:
        if len(filtered) == 0:
            st.info("Apply filters to see insights.")
        else:
            render_charts(filtered, candidates)


if __name__ == "__main__":
    main()
