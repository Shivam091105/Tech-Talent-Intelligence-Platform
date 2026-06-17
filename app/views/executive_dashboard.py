"""
Executive Dashboard — high-level KPIs and overview charts.
"""

import streamlit as st
from app.components.metrics_card import metric_card, page_header, section_header, empty_state
from app.components.chart_helpers import horizontal_bar, donut_chart, histogram
from app.components.filters import render_sidebar_filters
from database import queries


def render():
    page_header("Executive Dashboard", "High-level overview of the tech talent market")

    filters = render_sidebar_filters()
    country = filters["country"]
    source = filters["source_dataset"]

    try:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_df = queries.get_total_jobs(country=country, source_dataset=source)
            total = int(total_df.iloc[0]["total_jobs"]) if not total_df.empty else 0
            metric_card("Total Jobs", total)

        with col2:
            avg_df = queries.get_avg_salary(country=country, source_dataset=source)
            avg_sal = float(avg_df.iloc[0]["avg_salary"]) if not avg_df.empty and avg_df.iloc[0]["avg_salary"] else 0
            metric_card("Average Salary", avg_sal, prefix="$")

        with col3:
            top_skill_df = queries.get_top_skill(country=country, source_dataset=source)
            top_skill = top_skill_df.iloc[0]["skill_name"] if not top_skill_df.empty else "N/A"
            metric_card("Top Skill", top_skill)

        with col4:
            top_city_df = queries.get_top_hiring_city(country=country, source_dataset=source)
            top_city = top_city_df.iloc[0]["city"] if not top_city_df.empty else "N/A"
            metric_card("Top Hiring City", top_city)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Row 1
        col_left, col_right = st.columns(2)

        with col_left:
            section_header("Top 10 In-Demand Skills")
            skills_df = queries.get_top_skills(limit=10, country=country, source_dataset=source)
            if not skills_df.empty:
                fig = horizontal_bar(skills_df, x="job_count", y="skill_name")
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No skill data available")

        with col_right:
            section_header("Jobs by Work Mode")
            wm_df = queries.get_jobs_by_work_mode(country=country, source_dataset=source)
            if not wm_df.empty:
                fig = donut_chart(wm_df, values="job_count", names="work_mode")
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No work mode data available")

        # Charts Row 2
        col_left2, col_right2 = st.columns(2)

        with col_left2:
            section_header("Salary Distribution (USD)")
            sal_df = queries.get_salary_distribution(country=country, source_dataset=source)
            if not sal_df.empty:
                fig = histogram(sal_df, x="avg_salary_usd", nbins=40)
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No salary data available")

        with col_right2:
            section_header("Jobs by Experience Level")
            exp_df = queries.get_jobs_by_experience(country=country, source_dataset=source)
            if not exp_df.empty:
                fig = donut_chart(exp_df, values="job_count", names="level_name")
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No experience data available")

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.info("Make sure the database is running and the ETL pipeline has been executed.")
