"""
Location Intelligence — geographic hiring patterns.
"""

import streamlit as st
from app.components.metrics_card import page_header, section_header, empty_state
from app.components.chart_helpers import horizontal_bar, donut_chart, grouped_bar
from app.components.filters import render_sidebar_filters
from analytics import location_analytics
from app.theme import COLORS


def render():
    page_header("Location Intelligence", "Hiring distribution and skill demand across cities")

    filters = render_sidebar_filters()
    country = filters["country"]
    source = filters["source_dataset"]

    try:
        tab1, tab2, tab3 = st.tabs(["Top Cities", "Work Mode", "Skills by City"])

        with tab1:
            section_header("Top 15 Hiring Cities")
            cities_df = location_analytics.get_top_hiring_cities(limit=15, country=country, source_dataset=source)
            if not cities_df.empty:
                cities_df["city_label"] = cities_df["city"] + " (" + cities_df["country"].str[:3] + ")"
                fig = horizontal_bar(cities_df, x="job_count", y="city_label", color=COLORS["primary"])
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                section_header("Average Salary by City")
                salary_cities = cities_df[cities_df["avg_salary"].notna()].copy()
                if not salary_cities.empty:
                    fig2 = horizontal_bar(salary_cities, x="avg_salary", y="city_label", color=COLORS["secondary"])
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                empty_state("No city data available")

        with tab2:
            section_header("Remote vs Onsite vs Hybrid")
            wm_df = location_analytics.get_work_mode_distribution(country=country, source_dataset=source)
            if not wm_df.empty:
                col1, col2 = st.columns([1, 1])
                with col1:
                    fig = donut_chart(wm_df, values="job_count", names="work_mode")
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.markdown("#### Work Mode Breakdown")
                    total = wm_df["job_count"].sum()
                    for _, row in wm_df.iterrows():
                        mode = (row["work_mode"] or "Unknown").title()
                        count = row["job_count"]
                        pct = (count / total * 100) if total > 0 else 0
                        st.markdown(f"**{mode}**: {count:,} jobs ({pct:.1f}%)")
            else:
                empty_state("No work mode data available")

        with tab3:
            section_header("Top Skills by City", "Most demanded skills in each major city")
            skills_city_df = location_analytics.get_top_skills_per_city(
                limit_skills=5, country=country, source_dataset=source
            )
            if not skills_city_df.empty:
                fig = grouped_bar(skills_city_df, x="city", y="job_count", color="skill_name", barmode="group")
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("Not enough data for skills-by-city analysis")

    except Exception as e:
        st.error(f"Error loading location intelligence: {e}")
