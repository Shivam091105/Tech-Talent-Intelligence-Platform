"""
Reusable KPI metric card and section header components.
"""

import streamlit as st


def metric_card(label: str, value, prefix: str = "", suffix: str = ""):
    """
    Render a styled KPI metric card.

    Args:
        label: Metric description (e.g., "Total Jobs")
        value: Metric value (e.g., 22450)
        prefix: Text before value (e.g., "$")
        suffix: Text after value (e.g., "%")
    """
    if isinstance(value, (int, float)):
        formatted_value = f"{prefix}{value:,.0f}{suffix}"
    else:
        formatted_value = f"{prefix}{value}{suffix}"

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{formatted_value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a page title and subtitle."""
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_header(title: str, description: str = ""):
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    if description:
        st.caption(description)


def empty_state(message: str = "No data available"):
    """Show an empty state message when no data is available."""
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 1rem; color: #64748B;">
        <div style="font-size: 0.95rem;">{message}</div>
    </div>
    """, unsafe_allow_html=True)
