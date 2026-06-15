"""
Reusable KPI metric card component for the dashboard.
"""

import streamlit as st


def metric_card(label: str, value, icon: str = "📊", prefix: str = "", suffix: str = ""):
    """
    Render a styled KPI metric card.

    Args:
        label: Metric description (e.g., "Total Jobs")
        value: Metric value (e.g., 22450)
        icon: Emoji icon
        prefix: Text before value (e.g., "$")
        suffix: Text after value (e.g., "%")
    """
    formatted_value = f"{prefix}{value:,.0f}{suffix}" if isinstance(value, (int, float)) else f"{prefix}{value}{suffix}"

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{formatted_value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, description: str = ""):
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    if description:
        st.caption(description)


def empty_state(message: str = "No data available", icon: str = "📭"):
    """Show an empty state message when no data is available."""
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; color: #8892A0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <div style="font-size: 1.1rem;">{message}</div>
    </div>
    """, unsafe_allow_html=True)
