"""
Technology Trends — compare and track specific technologies.
"""

import streamlit as st
from app.components.metrics_card import page_header, section_header, empty_state
from app.components.chart_helpers import horizontal_bar, treemap
from app.components.filters import render_sidebar_filters
from analytics import trend_analytics
from app.theme import COLORS


TECH_GROUPS = {
    "Programming Languages": ["python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "ruby", "kotlin"],
    "Frontend Frameworks": ["react", "angular", "vue", "next.js", "svelte", "tailwind"],
    "Backend Frameworks": ["node.js", "spring", "django", "flask", "fastapi", "express", ".net"],
    "Cloud Platforms": ["aws", "azure", "gcp", "heroku", "digitalocean"],
    "Databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb"],
    "DevOps & Tools": ["docker", "kubernetes", "terraform", "jenkins", "ci/cd", "git", "linux"],
    "Data & AI": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "spark", "machine learning"],
}


def render():
    page_header("Technology Trends", "Compare technologies and explore the tech landscape")

    filters = render_sidebar_filters()
    country = filters["country"]
    source = filters["source_dataset"]

    try:
        tab1, tab2, tab3 = st.tabs(["Compare Technologies", "Technology Landscape", "Full Ranking"])

        with tab1:
            section_header("Head-to-Head Technology Comparison")
            group_choice = st.selectbox("Technology group", list(TECH_GROUPS.keys()))
            selected_techs = TECH_GROUPS[group_choice]

            comp_df = trend_analytics.compare_technologies(
                skills_list=selected_techs, country=country, source_dataset=source
            )
            if not comp_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Demand (Job Count)")
                    fig = horizontal_bar(comp_df, x="job_count", y="skill_name", color=COLORS["primary"])
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.markdown("#### Average Salary (USD)")
                    salary_df = comp_df[comp_df["avg_salary"].notna()].copy()
                    if not salary_df.empty:
                        fig = horizontal_bar(salary_df, x="avg_salary", y="skill_name", color=COLORS["secondary"])
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        empty_state("No salary data for selected technologies")
            else:
                empty_state("No data found for selected technologies")

        with tab2:
            section_header("Technology Landscape", "Skill ecosystem grouped by category")
            cat_df = trend_analytics.get_category_breakdown(country=country, source_dataset=source)
            if not cat_df.empty:
                fig = treemap(cat_df, path=["skill_category", "skill_name"], values="job_count")
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No category data available")

        with tab3:
            section_header("Complete Skill Ranking", "Top 30 most demanded skills")
            rank_df = trend_analytics.get_skill_ranking(limit=30, country=country, source_dataset=source)
            if not rank_df.empty:
                fig = horizontal_bar(rank_df, x="job_count", y="skill_name", color=COLORS["accent"])
                st.plotly_chart(fig, use_container_width=True)
                with st.expander("View full table"):
                    st.dataframe(rank_df, use_container_width=True, hide_index=True)
            else:
                empty_state("No ranking data available")

    except Exception as e:
        st.error(f"Error loading technology trends: {e}")
