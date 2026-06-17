"""Quick diagnostic to check India data completeness."""
import sys
sys.path.insert(0, ".")
from database.connection import execute_query_df

queries = {
    "Jobs by country": "SELECT l.country, COUNT(*) as job_count FROM jobs j JOIN locations l ON j.location_id = l.location_id GROUP BY l.country ORDER BY job_count DESC",
    "Jobs by source": "SELECT source_dataset, COUNT(*) as job_count FROM jobs GROUP BY source_dataset ORDER BY job_count DESC",
    "India skill links": "SELECT COUNT(*) as cnt FROM job_skills js JOIN jobs j ON js.job_id = j.job_id JOIN locations l ON j.location_id = l.location_id WHERE l.country = 'India'",
    "India salaries": "SELECT COUNT(*) as cnt FROM salaries s JOIN jobs j ON s.job_id = j.job_id JOIN locations l ON j.location_id = l.location_id WHERE l.country = 'India' AND s.avg_salary_usd > 0",
    "Total skill links": "SELECT COUNT(*) as cnt FROM job_skills",
    "Total salaries": "SELECT COUNT(*) as cnt FROM salaries WHERE avg_salary_usd > 0",
    "Sample India jobs": "SELECT j.job_id, j.job_title, l.city, j.source_dataset FROM jobs j JOIN locations l ON j.location_id = l.location_id WHERE l.country = 'India' LIMIT 5",
    "Skills per source": "SELECT j.source_dataset, COUNT(DISTINCT js.job_id) as jobs_with_skills, COUNT(*) as skill_links FROM job_skills js JOIN jobs j ON js.job_id = j.job_id GROUP BY j.source_dataset",
    "Salaries per source": "SELECT j.source_dataset, COUNT(*) as salary_count, ROUND(AVG(s.avg_salary_usd)::numeric, 2) as avg_sal FROM salaries s JOIN jobs j ON s.job_id = j.job_id WHERE s.avg_salary_usd > 0 GROUP BY j.source_dataset",
}

for label, q in queries.items():
    print(f"\n=== {label} ===")
    try:
        df = execute_query_df(q)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"ERROR: {e}")
