"""
Streamlit Theme — professional dark dashboard design.
No emojis. Clean typography. Enterprise aesthetic.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio


# ===========================================================================
# Color Palette
# ===========================================================================

COLORS = {
    "background": "#0E1117",
    "surface": "#161B22",
    "card_bg": "#1C2333",
    "card_border": "#2D3748",
    "primary": "#3B82F6",
    "secondary": "#10B981",
    "accent": "#8B5CF6",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#E2E8F0",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "border": "#1E293B",
    "chart_colors": [
        "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444",
        "#06B6D4", "#EC4899", "#84CC16", "#F97316", "#6366F1",
        "#14B8A6", "#F43F5E", "#A855F7", "#22D3EE", "#FB923C",
    ],
}


# ===========================================================================
# Custom CSS
# ===========================================================================

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ---- Hide Streamlit defaults ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* ---- Hide the auto-generated page nav at top of sidebar ---- */
    [data-testid="stSidebarNav"] {display: none !important;}
    section[data-testid="stSidebar"] > div > div:first-child > div:first-child {
        display: none !important;
    }

    /* ---- Layout ---- */
    .block-container {
        padding: 2rem 2.5rem 2rem 2.5rem;
        max-width: 1400px;
    }

    /* ---- Sidebar branding ---- */
    .sidebar-brand {
        text-align: center;
        padding: 1.5rem 0.5rem 0.5rem 0.5rem;
    }
    .sidebar-brand-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #E2E8F0;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    .sidebar-brand-subtitle {
        font-size: 0.75rem;
        font-weight: 400;
        color: #64748B;
        margin-top: 2px;
        letter-spacing: 0.02em;
    }

    /* ---- Radio navigation styling ---- */
    div[data-testid="stSidebar"] .stRadio > label {
        display: none !important;
    }
    div[data-testid="stSidebar"] .stRadio > div {
        gap: 2px;
    }
    div[data-testid="stSidebar"] .stRadio > div > label {
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        color: #94A3B8;
        transition: all 0.15s ease;
        cursor: pointer;
    }
    div[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(59, 130, 246, 0.08);
        color: #E2E8F0;
    }
    div[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    div[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(59, 130, 246, 0.12);
        color: #3B82F6;
        font-weight: 600;
    }

    /* ---- Metric cards ---- */
    .metric-card {
        background: #1C2333;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #E2E8F0;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* ---- Page titles ---- */
    .page-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #E2E8F0;
        margin-bottom: 2px;
        letter-spacing: -0.01em;
    }
    .page-subtitle {
        font-size: 0.875rem;
        color: #64748B;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    /* ---- Section headers ---- */
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2D3748;
    }

    /* ---- Skill badges (career advisor) ---- */
    .skill-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 3px 4px 3px 0;
    }
    .skill-tag.match {
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .skill-tag.gap {
        background: rgba(239, 68, 68, 0.1);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }

    /* ---- Score indicator ---- */
    .score-ring {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0 auto;
    }

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #2D3748;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        padding: 10px 20px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        color: #3B82F6 !important;
        border-bottom: 2px solid #3B82F6;
    }

    /* ---- Filter sidebar labels ---- */
    .filter-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        margin-top: 8px;
    }

    /* ---- Streamlit element overrides ---- */
    .stSelectbox label, .stMultiSelect label {
        font-size: 0.85rem !important;
        color: #94A3B8 !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---- Expander ---- */
    details {
        border: 1px solid #2D3748;
        border-radius: 8px;
    }
</style>
"""


# ===========================================================================
# Plotly Template
# ===========================================================================

def get_plotly_template():
    """Custom Plotly template matching the dashboard theme."""
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, -apple-system, sans-serif", color="#E2E8F0", size=12),
            title=dict(font=dict(size=14, color="#E2E8F0"), x=0, xanchor="left"),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                zerolinecolor="rgba(255,255,255,0.06)",
                tickfont=dict(color="#94A3B8", size=11),
                title_font=dict(color="#94A3B8", size=12),
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                zerolinecolor="rgba(255,255,255,0.06)",
                tickfont=dict(color="#94A3B8", size=11),
                title_font=dict(color="#94A3B8", size=12),
            ),
            colorway=COLORS["chart_colors"],
            hoverlabel=dict(
                bgcolor="#1C2333",
                bordercolor="#3B82F6",
                font=dict(color="#E2E8F0", family="Inter", size=12),
            ),
            legend=dict(
                font=dict(color="#94A3B8", size=11),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
            margin=dict(l=40, r=20, t=40, b=40),
        )
    )


def apply_theme():
    """Apply custom CSS and configure Plotly template."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    pio.templates["tech_talent"] = get_plotly_template()
    pio.templates.default = "tech_talent"
