"""
Module 2: Skill Intelligence — deep-dive into skill demand, co-occurrence, and salary.
"""

import streamlit as st
from app.components.metrics_card import section_header, empty_state
from app.components.chart_helpers import horizontal_bar, treemap, heatmap, scatter_plot
from app.components.filters import render_sidebar_filters
from analytics import skill_analytics


def render():
    st.markdown("## 💡 Skill Intelligence")
    st.caption("Understand what skills the market demands and how they relate to each other")

    filters = render_sidebar_filters()
    country = filters["country"]
    source = filters["source_dataset"]

    try:
        # Tab-based layout
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Top Skills", "🗂️ Skill Categories", "🔗 Co-occurrence", "💰 Demand vs Salary"
        ])

        # ---------------------------------------------------------------
        # Tab 1: Top Skills
        # ---------------------------------------------------------------
        with tab1:
            section_header("Top 20 Skills by Job Demand")
            df = skill_analytics.get_top_skills(limit=20, country=country, source_dataset=source)
            if not df.empty:
                fig = horizontal_bar(df, x="job_count", y="skill_name")
                st.plotly_chart(fig, use_container_width=True)

                # Data table
                with st.expander("📋 View Raw Data"):
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                empty_state("No skill data available")

        # ---------------------------------------------------------------
        # Tab 2: Skill Categories
        # ---------------------------------------------------------------
        with tab2:
            section_header("Skills by Category", "Explore the distribution of skills across technology categories")
            cat_df = skill_analytics.get_skills_by_category(country=country, source_dataset=source)
            if not cat_df.empty:
                fig = treemap(cat_df, path=["skill_category", "skill_name"], values="job_count")
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No category data available")

        # ---------------------------------------------------------------
        # Tab 3: Co-occurrence Heatmap
        # ---------------------------------------------------------------
        with tab3:
            section_header("Skill Co-occurrence Matrix",
                           "Which skills are most commonly required together?")

            top_n = st.slider("Number of skills to analyze", 8, 20, 12, key="cooccurrence_slider")
            matrix = skill_analytics.get_skill_cooccurrence_matrix(
                top_n=top_n, country=country, source_dataset=source
            )
            if not matrix.empty:
                fig = heatmap(matrix, title="")
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("Not enough data for co-occurrence analysis")

        # ---------------------------------------------------------------
        # Tab 4: Demand vs Salary Scatter
        # ---------------------------------------------------------------
        with tab4:
            section_header("Skill Demand vs Average Salary",
                           "Higher-right = high demand AND high salary (ideal skills to learn)")
            scatter_df = skill_analytics.get_skill_demand_vs_salary(
                limit=25, country=country, source_dataset=source
            )
            if not scatter_df.empty:
                fig = scatter_plot(
                    scatter_df, x="job_count", y="avg_salary",
                    text="skill_name", size="job_count",
                )
                fig.update_layout(
                    xaxis_title="Job Demand (count)",
                    yaxis_title="Average Salary (USD)",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No salary data available for scatter plot")

    except Exception as e:
        st.error(f"Error loading skill intelligence: {e}")
