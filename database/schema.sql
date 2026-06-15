-- ============================================================================
-- Tech Talent Intelligence Platform — Database Schema
-- ============================================================================
-- Normalized PostgreSQL schema for storing and analyzing tech job postings.
-- Run this file via: python scripts/setup_database.py
-- ============================================================================

-- ---------------------------------------------------------------------------
-- Drop existing tables (for clean re-initialization)
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS v_experience_summary CASCADE;
DROP VIEW IF EXISTS v_location_hiring CASCADE;
DROP VIEW IF EXISTS v_skill_demand CASCADE;
DROP TABLE IF EXISTS job_skills CASCADE;
DROP TABLE IF EXISTS salaries CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS experience_levels CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- ---------------------------------------------------------------------------
-- Reference Tables
-- ---------------------------------------------------------------------------

CREATE TABLE companies (
    company_id   SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_type VARCHAR(100),          -- e.g., "Product", "Service", "Startup"
    company_rating FLOAT                -- Glassdoor-style rating (1.0 - 5.0)
);

CREATE TABLE locations (
    location_id  SERIAL PRIMARY KEY,
    city         VARCHAR(150) NOT NULL,
    state        VARCHAR(150),
    country      VARCHAR(100) NOT NULL,
    UNIQUE (city, country)
);

CREATE TABLE experience_levels (
    level_id   SERIAL PRIMARY KEY,
    level_name VARCHAR(50) NOT NULL UNIQUE,  -- Entry, Mid, Senior, Lead
    min_years  INT NOT NULL,
    max_years  INT NOT NULL
);

CREATE TABLE skills (
    skill_id       SERIAL PRIMARY KEY,
    skill_name     VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(50) NOT NULL       -- language, framework, cloud, database, tool, soft_skill
);

-- ---------------------------------------------------------------------------
-- Core Fact Table
-- ---------------------------------------------------------------------------

CREATE TABLE jobs (
    job_id              SERIAL PRIMARY KEY,
    job_title           VARCHAR(255) NOT NULL,
    company_id          INT REFERENCES companies(company_id),
    location_id         INT REFERENCES locations(location_id),
    experience_level_id INT REFERENCES experience_levels(level_id),
    work_mode           VARCHAR(20),          -- remote, onsite, hybrid
    employment_type     VARCHAR(30),          -- full-time, contract, internship
    posted_date         DATE,
    source_dataset      VARCHAR(100) NOT NULL -- provenance: which CSV this came from
);

-- ---------------------------------------------------------------------------
-- Salary Table (1:1 with jobs)
-- ---------------------------------------------------------------------------

CREATE TABLE salaries (
    salary_id      SERIAL PRIMARY KEY,
    job_id         INT NOT NULL UNIQUE REFERENCES jobs(job_id) ON DELETE CASCADE,
    min_salary_usd FLOAT,
    max_salary_usd FLOAT,
    avg_salary_usd FLOAT NOT NULL
);

-- ---------------------------------------------------------------------------
-- Junction Table: Jobs <-> Skills (Many-to-Many)
-- ---------------------------------------------------------------------------

CREATE TABLE job_skills (
    job_id   INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_id INT NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- ---------------------------------------------------------------------------
-- Indexes for Analytical Query Performance
-- ---------------------------------------------------------------------------

CREATE INDEX idx_jobs_company        ON jobs(company_id);
CREATE INDEX idx_jobs_location       ON jobs(location_id);
CREATE INDEX idx_jobs_experience     ON jobs(experience_level_id);
CREATE INDEX idx_jobs_work_mode      ON jobs(work_mode);
CREATE INDEX idx_jobs_posted_date    ON jobs(posted_date);
CREATE INDEX idx_jobs_source         ON jobs(source_dataset);
CREATE INDEX idx_salaries_avg        ON salaries(avg_salary_usd);
CREATE INDEX idx_job_skills_skill    ON job_skills(skill_id);
CREATE INDEX idx_job_skills_job      ON job_skills(job_id);

-- ---------------------------------------------------------------------------
-- Analytical Views
-- ---------------------------------------------------------------------------

-- Skill demand summary: job count + average salary per skill
CREATE VIEW v_skill_demand AS
SELECT
    s.skill_id,
    s.skill_name,
    s.skill_category,
    COUNT(DISTINCT js.job_id) AS job_count,
    ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sal.avg_salary_usd)::numeric, 2) AS median_salary
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id
JOIN jobs j ON js.job_id = j.job_id
LEFT JOIN salaries sal ON j.job_id = sal.job_id
GROUP BY s.skill_id, s.skill_name, s.skill_category;

-- Location hiring summary
CREATE VIEW v_location_hiring AS
SELECT
    l.location_id,
    l.city,
    l.state,
    l.country,
    COUNT(*) AS job_count,
    ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary,
    ROUND(MIN(sal.avg_salary_usd)::numeric, 2) AS min_salary,
    ROUND(MAX(sal.avg_salary_usd)::numeric, 2) AS max_salary
FROM locations l
JOIN jobs j ON l.location_id = j.location_id
LEFT JOIN salaries sal ON j.job_id = sal.job_id
GROUP BY l.location_id, l.city, l.state, l.country;

-- Experience level summary
CREATE VIEW v_experience_summary AS
SELECT
    el.level_id,
    el.level_name,
    el.min_years,
    el.max_years,
    COUNT(*) AS job_count,
    ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary,
    ROUND(MIN(sal.avg_salary_usd)::numeric, 2) AS min_salary,
    ROUND(MAX(sal.avg_salary_usd)::numeric, 2) AS max_salary
FROM experience_levels el
JOIN jobs j ON el.level_id = j.experience_level_id
LEFT JOIN salaries sal ON j.job_id = sal.job_id
GROUP BY el.level_id, el.level_name, el.min_years, el.max_years;

-- ---------------------------------------------------------------------------
-- Seed reference data: experience levels
-- ---------------------------------------------------------------------------

INSERT INTO experience_levels (level_name, min_years, max_years) VALUES
    ('Entry',  0, 2),
    ('Mid',    3, 5),
    ('Senior', 6, 10),
    ('Lead',   10, 99)
ON CONFLICT (level_name) DO NOTHING;
