"""
Streamlit Theme — production-grade dark dashboard design.
Enterprise aesthetic. Clean typography. Zero emojis.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio


# ===========================================================================
# Color Palette
# ===========================================================================

COLORS = {
    "background": "#0B0F19",
    "surface": "#111827",
    "card_bg": "#1F2937",
    "card_border": "#374151",
    "primary": "#3B82F6",
    "secondary": "#10B981",
    "accent": "#8B5CF6",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#F1F5F9",
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
# Custom CSS — production-grade enterprise dashboard
# ===========================================================================

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ---- Base typography ---- */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ---- Hide Streamlit chrome ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: rgba(11, 15, 25, 0.8);
        backdrop-filter: blur(12px);
    }

    /* ---- Hide auto-generated page nav ---- */
    [data-testid="stSidebarNav"] {display: none !important;}
    nav[data-testid="stSidebarNav"] {display: none !important;}
    section[data-testid="stSidebar"] > div:first-child > div:first-child > div:first-child {
        display: none !important;
    }

    /* ---- Main content area ---- */
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 1440px;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: #111827 !important;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 0.5rem;
    }

    /* ---- Sidebar branding ---- */
    .sidebar-brand {
        text-align: center;
        padding: 1.25rem 1rem 0.75rem 1rem;
    }
    .sidebar-brand-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #F1F5F9;
        letter-spacing: -0.02em;
        line-height: 1.4;
    }
    .sidebar-brand-subtitle {
        font-size: 0.7rem;
        font-weight: 500;
        color: #64748B;
        margin-top: 2px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* ---- Radio navigation ---- */
    div[data-testid="stSidebar"] .stRadio > label {
        display: none !important;
    }
    div[data-testid="stSidebar"] .stRadio > div {
        gap: 1px;
        padding: 0 0.5rem;
    }
    div[data-testid="stSidebar"] .stRadio > div > label {
        padding: 0.55rem 0.75rem;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 500;
        color: #94A3B8;
        cursor: pointer;
        transition: all 0.12s ease;
        margin: 0;
    }
    div[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(59, 130, 246, 0.08);
        color: #CBD5E1;
    }
    div[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    div[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(59, 130, 246, 0.12);
        color: #3B82F6;
        font-weight: 600;
    }

    /* ---- Metric cards ---- */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        flex: 1;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1.2;
        margin-bottom: 4px;
        font-variant-numeric: tabular-nums;
    }
    .metric-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* ---- Page header ---- */
    .page-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }
    .page-subtitle {
        font-size: 0.82rem;
        color: #64748B;
        margin-bottom: 1.25rem;
        font-weight: 400;
        line-height: 1.4;
    }

    /* ---- Section headers ---- */
    .section-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #1E293B;
    }

    /* ---- Skill tags ---- */
    .skill-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }
    .skill-tag.match {
        background: rgba(16, 185, 129, 0.1);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .skill-tag.gap {
        background: rgba(239, 68, 68, 0.08);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.15);
    }

    /* ---- Score indicator ---- */
    .score-ring {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 auto;
    }

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #1E293B;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        padding: 0.6rem 1.25rem;
        font-size: 0.82rem;
        font-weight: 500;
        color: #94A3B8;
        background: transparent;
        border-bottom: 2px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #CBD5E1;
    }
    .stTabs [aria-selected="true"] {
        color: #3B82F6 !important;
        border-bottom: 2px solid #3B82F6 !important;
        background: transparent !important;
    }

    /* ---- Filter sidebar labels ---- */
    .filter-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
        margin-top: 4px;
    }

    /* ---- Selectbox / multiselect overrides ---- */
    .stSelectbox label, .stMultiSelect label {
        font-size: 0.82rem !important;
        color: #94A3B8 !important;
    }

    /* ---- Streamlit metrics (st.metric) ---- */
    div[data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-variant-numeric: tabular-nums;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem !important;
    }

    /* ---- Expander ---- */
    details {
        border: 1px solid #1E293B !important;
        border-radius: 6px !important;
        background: transparent !important;
    }
    details summary {
        font-size: 0.82rem;
        font-weight: 500;
        color: #94A3B8;
    }

    /* ---- Dataframe ---- */
    .stDataFrame {
        border: 1px solid #1E293B;
        border-radius: 6px;
    }

    /* ---- Button ---- */
    .stButton > button[kind="primary"] {
        background: #3B82F6;
        border: none;
        font-weight: 600;
        font-size: 0.82rem;
        letter-spacing: 0.02em;
    }

    /* ---- Slider ---- */
    .stSlider label {
        font-size: 0.82rem !important;
        color: #94A3B8 !important;
    }

    /* ---- Toggle ---- */
    .stToggle label span {
        font-size: 0.82rem !important;
    }

    /* ---- CV Results Table ---- */
    .cv-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        margin-top: 0.5rem;
    }
    .cv-table th {
        text-align: left;
        padding: 8px 12px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 1px solid #374151;
    }
    .cv-table td {
        padding: 6px 12px;
        color: #E2E8F0;
        border-bottom: 1px solid #1E293B;
        font-variant-numeric: tabular-nums;
    }
    .cv-table tr:last-child td {
        border-bottom: none;
        font-weight: 600;
        color: #3B82F6;
    }

    /* ---- Remove extra whitespace ---- */
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0;
    }

    /* ---- Horizontal rule ---- */
    hr {
        border: none;
        border-top: 1px solid #1E293B;
        margin: 1rem 0;
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
            title=dict(font=dict(size=13, color="#E2E8F0"), x=0, xanchor="left"),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.04)",
                zerolinecolor="rgba(255,255,255,0.04)",
                tickfont=dict(color="#94A3B8", size=11),
                title_font=dict(color="#94A3B8", size=11),
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.04)",
                zerolinecolor="rgba(255,255,255,0.04)",
                tickfont=dict(color="#94A3B8", size=11),
                title_font=dict(color="#94A3B8", size=11),
            ),
            colorway=COLORS["chart_colors"],
            hoverlabel=dict(
                bgcolor="#1F2937",
                bordercolor="#374151",
                font=dict(color="#F1F5F9", family="Inter", size=12),
            ),
            legend=dict(
                font=dict(color="#94A3B8", size=11),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
            margin=dict(l=40, r=20, t=36, b=36),
        )
    )


def apply_theme():
    """Apply custom CSS and configure Plotly template."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    pio.templates["tech_talent"] = get_plotly_template()
    pio.templates.default = "tech_talent"
