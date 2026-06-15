"""
Chart helper functions — wraps Plotly charts with consistent styling.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from app.theme import COLORS


def horizontal_bar(df: pd.DataFrame, x: str, y: str, title: str = "", color: str = None, text_auto: bool = True):
    """Create a styled horizontal bar chart."""
    color = color or COLORS["primary"]
    fig = px.bar(
        df, x=x, y=y, orientation="h", title=title, text_auto=".2s" if text_auto else False,
        color_discrete_sequence=[color],
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed", title=""),
        xaxis=dict(title=""),
        height=max(400, len(df) * 28),
        showlegend=False,
    )
    fig.update_traces(
        marker=dict(cornerradius=5, line=dict(width=0)),
        textposition="outside",
        textfont=dict(size=11),
    )
    return fig


def donut_chart(df: pd.DataFrame, values: str, names: str, title: str = ""):
    """Create a styled donut chart."""
    fig = px.pie(
        df, values=values, names=names, title=title, hole=0.55,
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont=dict(size=11),
        pull=[0.03] * len(df),
    )
    fig.update_layout(
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        showlegend=True,
    )
    return fig


def histogram(df: pd.DataFrame, x: str, title: str = "", nbins: int = 30, color: str = None):
    """Create a styled histogram."""
    color = color or COLORS["primary"]
    fig = px.histogram(
        df, x=x, title=title, nbins=nbins,
        color_discrete_sequence=[color],
        opacity=0.85,
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Count",
        height=400,
        bargap=0.05,
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color="#0E1117")))
    return fig


def box_plot(df: pd.DataFrame, x: str, y: str, title: str = ""):
    """Create a styled box plot."""
    fig = px.box(
        df, x=x, y=y, title=title,
        color=x,
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_layout(
        height=450,
        showlegend=False,
        xaxis_title="",
        yaxis_title="",
    )
    return fig


def scatter_plot(df: pd.DataFrame, x: str, y: str, text: str = None, size: str = None, title: str = ""):
    """Create a styled scatter plot."""
    fig = px.scatter(
        df, x=x, y=y, text=text, size=size, title=title,
        color_discrete_sequence=[COLORS["secondary"]],
    )
    if text:
        fig.update_traces(
            textposition="top center",
            textfont=dict(size=10, color="#8892A0"),
        )
    fig.update_layout(height=450)
    return fig


def heatmap(matrix: pd.DataFrame, title: str = ""):
    """Create a styled heatmap from a square DataFrame."""
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=matrix.columns.tolist(),
        y=matrix.index.tolist(),
        colorscale=[
            [0, "#0E1117"],
            [0.5, "#4F8BF9"],
            [1, "#A78BFA"],
        ],
        hoverongaps=False,
        text=matrix.values,
        texttemplate="%{text}",
        textfont=dict(size=9),
    ))
    fig.update_layout(
        title=title,
        height=max(500, len(matrix) * 35),
        xaxis=dict(tickangle=45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


def treemap(df: pd.DataFrame, path: list, values: str, title: str = ""):
    """Create a styled treemap."""
    fig = px.treemap(
        df, path=path, values=values, title=title,
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_layout(height=500)
    fig.update_traces(
        textinfo="label+value",
        textfont=dict(size=12),
    )
    return fig


def grouped_bar(df: pd.DataFrame, x: str, y: str, color: str, title: str = "", barmode: str = "group"):
    """Create a grouped or stacked bar chart."""
    fig = px.bar(
        df, x=x, y=y, color=color, title=title,
        barmode=barmode,
        color_discrete_sequence=COLORS["chart_colors"],
    )
    fig.update_layout(
        height=450,
        xaxis_title="",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )
    fig.update_traces(marker=dict(cornerradius=4))
    return fig
