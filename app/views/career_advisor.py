"""
Career Advisor — rule-based skill gap analysis and salary estimation.
"""

import streamlit as st
from app.components.metrics_card import page_header, section_header, empty_state
from app.components.chart_helpers import horizontal_bar
from app.theme import COLORS


def render():
    page_header("Career Advisor", "Skill gap analysis and salary estimates based on your profile")

    try:
        from analytics import career_advisor

        # -----------------------------------------------------------
        # User Input
        # -----------------------------------------------------------
        section_header("Your Profile")

        col1, col2 = st.columns(2)

        with col1:
            all_skills_df = career_advisor.get_all_skills()
            skill_options = all_skills_df["skill_name"].tolist() if not all_skills_df.empty else []
            user_skills = st.multiselect(
                "Current skills",
                options=skill_options,
                default=None,
                placeholder="Start typing to search skills...",
            )

        with col2:
            experience_level = st.selectbox("Experience level", ["Entry", "Mid", "Senior", "Lead"])
            is_india = st.toggle("Targeting Indian market", value=True)

        # -----------------------------------------------------------
        # Analyze
        # -----------------------------------------------------------
        if st.button("Analyze Profile", type="primary", use_container_width=True):
            if not user_skills:
                st.warning("Select at least one skill to analyze.")
                return

            with st.spinner("Analyzing..."):
                result = career_advisor.analyze_skill_gap(
                    user_skills=user_skills,
                    experience_level=experience_level,
                    limit=20,
                )

            st.markdown("---")

            # -----------------------------------------------------------
            # Market Readiness Score
            # -----------------------------------------------------------
            section_header("Market Readiness")

            score = result["match_percentage"]
            if score >= 70:
                score_color = COLORS["secondary"]
            elif score >= 40:
                score_color = COLORS["warning"]
            else:
                score_color = COLORS["danger"]

            col_score, col_details = st.columns([1, 2])

            with col_score:
                st.markdown(f"""
                <div class="score-ring" style="border: 3px solid {score_color}; color: {score_color};">
                    {score:.0f}%
                </div>
                <p style="text-align: center; color: #64748B; margin-top: 0.5rem; font-size: 0.85rem;">
                    Market Match
                </p>
                """, unsafe_allow_html=True)

            with col_details:
                st.markdown(f"""
                | Metric | Value |
                |---|---|
                | Skills matched | {len(result['matching_skills'])} |
                | Skills to learn | {len(result['missing_skills'])} |
                | Experience level | {experience_level} |
                """)

            st.markdown("---")

            # -----------------------------------------------------------
            # Matching vs Missing Skills
            # -----------------------------------------------------------
            col_match, col_gap = st.columns(2)

            with col_match:
                section_header("Skills You Have (In Demand)")
                if result["matching_skills"]:
                    for skill in result["matching_skills"]:
                        demand = skill.get("job_count", 0)
                        salary = skill.get("avg_salary")
                        salary_str = f" | ${salary:,.0f} avg" if salary else ""
                        st.markdown(
                            f'<span class="skill-tag match">{skill["skill_name"]}</span>'
                            f' <small style="color: #64748B;">{demand} jobs{salary_str}</small>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("None of your current skills are in the top market demand for this level.")

            with col_gap:
                section_header("Recommended Skills to Learn")
                if result["missing_skills"]:
                    for skill in result["missing_skills"][:10]:
                        demand = skill.get("job_count", 0)
                        salary = skill.get("avg_salary")
                        salary_str = f" | ${salary:,.0f} avg" if salary else ""
                        st.markdown(
                            f'<span class="skill-tag gap">{skill["skill_name"]}</span>'
                            f' <small style="color: #64748B;">{demand} jobs{salary_str}</small>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.success("You have all the top demanded skills for this level.")

            st.markdown("---")

            # -----------------------------------------------------------
            # Salary Prediction
            # -----------------------------------------------------------
            section_header("Salary Estimate")

            try:
                from ml.salary_predictor import predict_salary

                prediction = predict_salary(
                    skills=user_skills,
                    experience_level=experience_level,
                    is_india=is_india,
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Low Estimate", f"${prediction['salary_low']:,.0f}")
                with col2:
                    st.metric("Expected Salary", f"${prediction['predicted_salary']:,.0f}")
                with col3:
                    st.metric("High Estimate", f"${prediction['salary_high']:,.0f}")

                st.caption(f"Confidence: {prediction['confidence']}  |  Random Forest model trained on market data")

            except FileNotFoundError:
                st.info("Salary prediction model not trained yet. Run `python scripts/train_model.py` to enable.")
            except Exception as e:
                st.warning(f"Could not generate salary prediction: {e}")

            # -----------------------------------------------------------
            # Matching Roles
            # -----------------------------------------------------------
            st.markdown("---")
            section_header("Matching Job Roles")

            roles_df = career_advisor.find_matching_roles(user_skills=user_skills)
            if not roles_df.empty:
                fig = horizontal_bar(
                    roles_df.head(10), x="matching_skills", y="job_title",
                    color=COLORS["accent"],
                )
                fig.update_layout(xaxis_title="Matching Skills Count")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No matching roles found. Try selecting more skills.")

    except Exception as e:
        st.error(f"Error loading career advisor: {e}")
        st.info("Make sure the database is running and the ETL pipeline has been executed.")
