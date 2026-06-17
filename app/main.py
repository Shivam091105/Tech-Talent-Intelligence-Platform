"""
Tech Talent Intelligence Platform — Streamlit Application Entry Point.

Run with: streamlit run app/main.py
"""

import sys
from pathlib import Path

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.theme import apply_theme

# ---------------------------------------------------------------------------
# Page Configuration (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Tech Talent Intelligence Platform",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom theme
apply_theme()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-title">Tech Talent Intelligence</div>
    <div class="sidebar-brand-subtitle">Analytics Platform</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation — single clean list, no duplicates
page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Skill Intelligence",
        "Salary Intelligence",
        "Location Intelligence",
        "Experience Intelligence",
        "Technology Trends",
        "Career Advisor",
    ],
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------------
# Page Routing — imports from 'views' (not 'pages') to avoid Streamlit
# auto-generating a second navigation from the pages/ directory.
# ---------------------------------------------------------------------------
if page == "Executive Dashboard":
    from app.views import executive_dashboard
    executive_dashboard.render()

elif page == "Skill Intelligence":
    from app.views import skill_intelligence
    skill_intelligence.render()

elif page == "Salary Intelligence":
    from app.views import salary_intelligence
    salary_intelligence.render()

elif page == "Location Intelligence":
    from app.views import location_intelligence
    location_intelligence.render()

elif page == "Experience Intelligence":
    from app.views import experience_intelligence
    experience_intelligence.render()

elif page == "Technology Trends":
    from app.views import tech_trends
    tech_trends.render()

elif page == "Career Advisor":
    from app.views import career_advisor
    career_advisor.render()
