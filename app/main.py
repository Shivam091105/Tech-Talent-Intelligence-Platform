"""
Tech Talent Intelligence Platform — Streamlit Application Entry Point.

This is the main file that configures the app and sets up multi-page navigation.
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
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Tech Talent Intelligence Platform — Analyzing 22,000+ tech job postings",
    },
)

# Apply custom theme
apply_theme()

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <div style="font-size: 2rem;">🧠</div>
    <div style="font-size: 1.1rem; font-weight: 700; color: #F1F5F9; margin-top: 0.25rem;">
        Tech Talent Intelligence
    </div>
    <div style="font-size: 0.75rem; color: #8892A0; margin-top: 0.25rem;">
        Platform v1.0
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "📊 Navigation",
    [
        "🏠 Executive Dashboard",
        "💡 Skill Intelligence",
        "💰 Salary Intelligence",
        "📍 Location Intelligence",
        "🎯 Experience Intelligence",
        "📈 Technology Trends",
        "🧭 Career Advisor",
    ],
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------------
# Page Routing
# ---------------------------------------------------------------------------
if page == "🏠 Executive Dashboard":
    from app.pages import executive_dashboard
    executive_dashboard.render()

elif page == "💡 Skill Intelligence":
    from app.pages import skill_intelligence
    skill_intelligence.render()

elif page == "💰 Salary Intelligence":
    from app.pages import salary_intelligence
    salary_intelligence.render()

elif page == "📍 Location Intelligence":
    from app.pages import location_intelligence
    location_intelligence.render()

elif page == "🎯 Experience Intelligence":
    from app.pages import experience_intelligence
    experience_intelligence.render()

elif page == "📈 Technology Trends":
    from app.pages import tech_trends
    tech_trends.render()

elif page == "🧭 Career Advisor":
    from app.pages import career_advisor
    career_advisor.render()
