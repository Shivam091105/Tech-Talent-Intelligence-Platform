"""
Module 3: Salary Intelligence — salary distributions, comparisons, and analysis.
"""

import streamlit as st
from app.components.metrics_card import section_header, empty_state
from app.components.chart_helpers import horizontal_bar, histogram, box_plot, grouped_bar
from app.components.filters import render_sidebar_filters
from analytics import salary_analytics
from app.theme import COLORS


def render():
    st.markdown("## 💰 Salary Intelligence")
    st.caption("Analyze compensation trends across skills, locations, and experience levels")

    filters = render_sidebar_filters()
    country = filters["country"]
    source = filters["source_dataset"]

    try:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Distribution", "💡 By Skill", "📍 By Location", "🎯 By Experience"
        ])

        # ---------------------------------------------------------------
        # Tab 1: Salary Distribution
        # ---------------------------------------------------------------
        with tab1:
            section_header("Salary Distribution (USD)")
            sal_df = salary_analytics.get_salary_distribution(country=country, source_dataset=source)
            if not sal_df.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Median", f"${sal_df['avg_salary_usd'].median():,.0f}")
                with col2:
                    st.metric("Mean", f"${sal_df['avg_salary_usd'].mean():,.0f}")
                with col3:
                    st.metric("Std Dev", f"${sal_df['avg_salary_usd'].std():,.0f}")

                fig = histogram(sal_df, x="avg_salary_usd", nbins=50, color=COLORS["secondary"])
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("No salary data available")

        # ---------------------------------------------------------------
        # Tab 2: Salary by Skill
        # ---------------------------------------------------------------
        with tab2:
            section_header("Top Paying Skills", "Skills with the highest average salaries (min 5 job postings)")
            skill_sal_df = salary_analytics.get_top_paying_skills(
                limit=15, country=country, source_dataset=source
            )
            if not skill_sal_df.empty:
                fig = horizontal_bar(
                    skill_sal_df, x="avg_salary", y="skill_name",
                    color=COLORS["secondary"],
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 View Details"):
                    st.dataframe(skill_sal_df, use_container_width=True, hide_index=True)
            else:
                empty_state("Not enough data for salary-by-skill analysis")

        # ---------------------------------------------------------------
        # Tab 3: Salary by Location
        # ---------------------------------------------------------------
        with tab3:
            section_header("Average Salary by City")
            city_sal_df = salary_analytics.get_salary_by_city(
                limit=15, country=country, source_dataset=source
            )
            if not city_sal_df.empty:
                fig = horizontal_bar(
                    city_sal_df, x="avg_salary", y="city",
                    color=COLORS["accent"],
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("Not enough data for salary-by-city analysis")

        # ---------------------------------------------------------------
        # Tab 4: Salary by Experience
        # ---------------------------------------------------------------
        with tab4:
            section_header("Salary Distribution by Experience Level")
            exp_sal_df = salary_analytics.get_salary_by_experience(
                country=country, source_dataset=source
            )
            if not exp_sal_df.empty:
                fig = box_plot(exp_sal_df, x="level_name", y="avg_salary_usd")
                fig.update_layout(xaxis_title="Experience Level", yaxis_title="Salary (USD)")
                st.plotly_chart(fig, use_container_width=True)

                # Also show work mode comparison
                st.markdown("---")
                section_header("Salary by Work Mode")
                wm_sal_df = salary_analytics.get_salary_by_work_mode(
                    country=country, source_dataset=source
                )
                if not wm_sal_df.empty:
                    fig2 = horizontal_bar(wm_sal_df, x="avg_salary", y="work_mode", color=COLORS["warning"])
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                empty_state("Not enough data for salary-by-experience analysis")

    except Exception as e:
        st.error(f"Error loading salary intelligence: {e}")
