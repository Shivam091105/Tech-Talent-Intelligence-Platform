"""
Module 7: Career Advisor — rule-based skill gap analysis + ML salary prediction.
"""

import streamlit as st
from app.components.metrics_card import section_header, empty_state
from app.components.chart_helpers import horizontal_bar
from app.theme import COLORS


def render():
    st.markdown("## 🧭 Career Advisor")
    st.caption("Get personalized skill recommendations and salary estimates based on your profile")

    try:
        from analytics import career_advisor

        # ---------------------------------------------------------------
        # User Input Form
        # ---------------------------------------------------------------
        st.markdown("### 📝 Your Profile")

        col1, col2 = st.columns(2)

        with col1:
            # Get all skills for the multi-select
            all_skills_df = career_advisor.get_all_skills()
            skill_options = all_skills_df["skill_name"].tolist() if not all_skills_df.empty else []

            user_skills = st.multiselect(
                "Select your current skills",
                options=skill_options,
                default=None,
                placeholder="Start typing to search skills...",
                help="Select all the technical skills you currently possess",
            )

        with col2:
            experience_level = st.selectbox(
                "Your experience level",
                ["Entry", "Mid", "Senior", "Lead"],
                index=0,
            )

            is_india = st.toggle("🇮🇳 Targeting Indian market", value=True)

        # ---------------------------------------------------------------
        # Analysis Button
        # ---------------------------------------------------------------
        if st.button("🔍 Analyze My Profile", type="primary", use_container_width=True):
            if not user_skills:
                st.warning("Please select at least one skill to analyze.")
                return

            with st.spinner("Analyzing your profile against market data..."):
                # Run skill gap analysis
                result = career_advisor.analyze_skill_gap(
                    user_skills=user_skills,
                    experience_level=experience_level,
                    limit=20,
                )

            st.markdown("---")

            # -----------------------------------------------------------
            # Market Readiness Score
            # -----------------------------------------------------------
            st.markdown("### 📊 Market Readiness Score")

            score = result["match_percentage"]
            score_color = COLORS["success"] if score >= 70 else (COLORS["warning"] if score >= 40 else COLORS["danger"])

            col_score, col_details = st.columns([1, 2])

            with col_score:
                st.markdown(f"""
                <div class="score-circle" style="border: 4px solid {score_color}; color: {score_color};">
                    {score:.0f}%
                </div>
                <p style="text-align: center; color: #8892A0; margin-top: 0.5rem;">
                    Market Match
                </p>
                """, unsafe_allow_html=True)

            with col_details:
                st.markdown(f"""
                - **Skills you have**: {len(result['matching_skills'])}
                - **Skills you need**: {len(result['missing_skills'])}
                - **Experience level**: {experience_level}
                """)

            st.markdown("---")

            # -----------------------------------------------------------
            # Matching Skills
            # -----------------------------------------------------------
            col_match, col_missing = st.columns(2)

            with col_match:
                st.markdown("### ✅ Skills You Have (In Demand)")
                if result["matching_skills"]:
                    for skill in result["matching_skills"]:
                        demand = skill.get("job_count", 0)
                        salary = skill.get("avg_salary")
                        salary_str = f" | ${salary:,.0f} avg" if salary else ""
                        st.markdown(
                            f'<span class="skill-badge match">{skill["skill_name"]}</span>'
                            f' <small style="color: #8892A0;">{demand} jobs{salary_str}</small>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("None of your skills are in the top market demand for this level.")

            # -----------------------------------------------------------
            # Missing Skills (Recommendations)
            # -----------------------------------------------------------
            with col_missing:
                st.markdown("### ❌ Skills to Learn (Recommended)")
                if result["missing_skills"]:
                    for skill in result["missing_skills"][:10]:
                        demand = skill.get("job_count", 0)
                        salary = skill.get("avg_salary")
                        salary_str = f" | ${salary:,.0f} avg" if salary else ""
                        st.markdown(
                            f'<span class="skill-badge missing">{skill["skill_name"]}</span>'
                            f' <small style="color: #8892A0;">{demand} jobs{salary_str}</small>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.success("You have all the top skills! 🎉")

            st.markdown("---")

            # -----------------------------------------------------------
            # Salary Prediction
            # -----------------------------------------------------------
            st.markdown("### 💰 Salary Estimate")

            try:
                from ml.salary_predictor import predict_salary

                prediction = predict_salary(
                    skills=user_skills,
                    experience_level=experience_level,
                    is_india=is_india,
                )

                col_sal1, col_sal2, col_sal3 = st.columns(3)
                with col_sal1:
                    st.metric("Low Estimate", f"${prediction['salary_low']:,.0f}")
                with col_sal2:
                    st.metric("Expected Salary", f"${prediction['predicted_salary']:,.0f}")
                with col_sal3:
                    st.metric("High Estimate", f"${prediction['salary_high']:,.0f}")

                st.caption(f"Confidence: {prediction['confidence']} | Based on Random Forest model trained on market data")

            except FileNotFoundError:
                st.info("💡 Salary prediction model not trained yet. Run `python scripts/train_model.py` to enable predictions.")
            except Exception as e:
                st.warning(f"Could not generate salary prediction: {e}")

            # -----------------------------------------------------------
            # Matching Roles
            # -----------------------------------------------------------
            st.markdown("---")
            st.markdown("### 🎯 Matching Job Roles")

            roles_df = career_advisor.find_matching_roles(user_skills=user_skills)
            if not roles_df.empty:
                fig = horizontal_bar(
                    roles_df.head(10), x="matching_skills", y="job_title",
                    color=COLORS["accent"],
                )
                fig.update_layout(xaxis_title="Matching Skills Count")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No matching roles found. Try selecting more skills.")

    except Exception as e:
        st.error(f"Error loading career advisor: {e}")
        st.info("Make sure the database is running and the ETL pipeline has been executed.")
