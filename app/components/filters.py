"""
Sidebar filter components — clean, professional labels.
"""

import streamlit as st
from database import queries


def render_sidebar_filters() -> dict:
    """
    Render sidebar filter widgets and return selected filter values.

    Returns:
        dict with keys: country, source_dataset
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="filter-label">FILTERS</div>', unsafe_allow_html=True)

    # India-specific toggle
    india_only = st.sidebar.toggle("India Only", value=False, help="Show only Indian market data")

    country = None
    if india_only:
        country = "India"
    else:
        try:
            countries_df = queries.get_unique_countries()
            country_options = ["All Countries"] + countries_df["country"].tolist()
            selected = st.sidebar.selectbox("Country", country_options, label_visibility="collapsed")
            country = None if selected == "All Countries" else selected
        except Exception:
            pass

    # Source dataset filter
    source_dataset = None
    try:
        sources_df = queries.get_source_datasets()
        source_options = ["All Datasets"] + sources_df["source_dataset"].tolist()
        selected_source = st.sidebar.selectbox("Data Source", source_options, label_visibility="collapsed")
        source_dataset = None if selected_source == "All Datasets" else selected_source
    except Exception:
        pass

    st.sidebar.markdown("---")

    return {
        "country": country,
        "source_dataset": source_dataset,
    }
