"""
Streamlit Theme — custom CSS and Plotly template for a premium dark dashboard look.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio


# ===========================================================================
# Color Palette
# ===========================================================================

COLORS = {
    "background": "#0E1117",
    "card_bg": "#1A1F2E",
    "card_border": "#2A3040",
    "primary": "#4F8BF9",
    "secondary": "#00D4AA",
    "accent": "#A78BFA",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#F1F5F9",
    "text_muted": "#8892A0",
    "chart_colors": [
        "#4F8BF9", "#00D4AA", "#A78BFA", "#F59E0B", "#EF4444",
        "#06B6D4", "#EC4899", "#84CC16", "#F97316", "#8B5CF6",
        "#14B8A6", "#F43F5E", "#6366F1", "#10B981", "#E879F9",
    ],
}


# ===========================================================================
# Custom CSS
# ===========================================================================

CUSTOM_CSS = """
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #1E2433 100%);
        border: 1px solid #2A3040;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 139, 249, 0.15);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #8892A0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4F8BF9;
        display: inline-block;
    }

    /* Chart container */
    .chart-container {
        background: #1A1F2E;
        border: 1px solid #2A3040;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }

    /* Badge / tag */
    .skill-badge {
        display: inline-block;
        background: rgba(79, 139, 249, 0.15);
        color: #4F8BF9;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 3px;
        border: 1px solid rgba(79, 139, 249, 0.3);
    }

    .skill-badge.missing {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border-color: rgba(239, 68, 68, 0.3);
    }

    .skill-badge.match {
        background: rgba(34, 197, 94, 0.15);
        color: #22C55E;
        border-color: rgba(34, 197, 94, 0.3);
    }

    /* Score circle */
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 auto;
    }
</style>
"""


# ===========================================================================
# Plotly Template
# ===========================================================================

def get_plotly_template():
    """Return a custom Plotly template matching the dashboard theme."""
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#F1F5F9", size=12),
            title=dict(font=dict(size=16, color="#F1F5F9")),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.08)",
                zerolinecolor="rgba(255,255,255,0.1)",
                tickfont=dict(color="#8892A0"),
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.08)",
                zerolinecolor="rgba(255,255,255,0.1)",
                tickfont=dict(color="#8892A0"),
            ),
            colorway=COLORS["chart_colors"],
            hoverlabel=dict(
                bgcolor="#1A1F2E",
                bordercolor="#4F8BF9",
                font=dict(color="#F1F5F9", family="Inter"),
            ),
            legend=dict(font=dict(color="#8892A0")),
            margin=dict(l=40, r=20, t=40, b=40),
        )
    )


def apply_theme():
    """Apply custom CSS and configure Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    # Register custom plotly template
    pio.templates["tech_talent"] = get_plotly_template()
    pio.templates.default = "tech_talent"
