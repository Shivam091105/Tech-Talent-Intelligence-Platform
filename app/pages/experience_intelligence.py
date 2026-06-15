"""
Module 5: Experience Intelligence — career-level analysis.
"""

import streamlit as st
from app.components.metrics_card import section_header, empty_state
from app.components.chart_helpers import donut_chart, box_plot, grouped_bar
from app.components.filters import render_sidebar_filters
from analytics import experience_analytics
from app.theme import COLORS


def render():
    st.markdown("## 🎯 Experience Intelligence")
    st.caption("Understand demand and compensation patterns across career levels")

    filters = render_sidebar_filters()
    country = filters["country"]
    source = filters["source_dataset"]

    try:
        tab1, tab2, tab3 = st.tabs([
            "📊 Distribution", "💡 Skills by Level", "🏠 Work Mode by Level"
        ])

        # ---------------------------------------------------------------
        # Tab 1: Experience Distribution + Salary
        # ---------------------------------------------------------------
        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                section_header("Job Demand by Experience Level")
                dist_df = experience_analytics.get_experience_distribution(
                    country=country, source_dataset=source
                )
                if not dist_df.empty:
                    fig = donut_chart(dist_df, values="job_count", names="level_name")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    empty_state("No experience data available")

            with col2:
                section_header("Salary by Experience Level")
                sal_df = experience_analytics.get_salary_by_experience(
                    country=country, source_dataset=source
                )
                if not sal_df.empty:
                    fig = box_plot(sal_df, x="level_name", y="avg_salary_usd")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    empty_state("No salary data available")

        # ---------------------------------------------------------------
        # Tab 2: Skills by Experience Level
        # ---------------------------------------------------------------
        with tab2:
            section_header("Top Skills per Experience Level",
                           "See how skill requirements change as you progress in your career")
            skills_df = experience_analytics.get_skills_by_experience(
                limit_skills=8, country=country, source_dataset=source
            )
            if not skills_df.empty:
                fig = grouped_bar(
                    skills_df, x="level_name", y="job_count",
                    color="skill_name", barmode="group",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("Not enough data for skills-by-experience analysis")

        # ---------------------------------------------------------------
        # Tab 3: Work Mode by Experience
        # ---------------------------------------------------------------
        with tab3:
            section_header("Work Mode Preferences by Experience Level",
                           "Do senior engineers get more remote opportunities?")
            wm_df = experience_analytics.get_work_mode_by_experience(
                country=country, source_dataset=source
            )
            if not wm_df.empty:
                fig = grouped_bar(
                    wm_df, x="level_name", y="job_count",
                    color="work_mode", barmode="stack",
                    title="",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("Not enough data for work-mode-by-experience analysis")

    except Exception as e:
        st.error(f"Error loading experience intelligence: {e}")
