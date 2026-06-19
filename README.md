# 🧠 Tech Talent Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

An end-to-end analytics platform that processes **20,000+ tech job postings** from multiple data sources and generates actionable intelligence about skill demand, salary trends, hiring patterns, and career recommendations.

> Built as a production-grade portfolio project showcasing Data Engineering, SQL, Machine Learning, and Software Engineering skills.

---

## 🎯 What This Platform Does

| Question | Module |
|---|---|
| What technologies are most in demand? | Skill Intelligence |
| Which skills pay the highest salaries? | Salary Intelligence |
| Which cities have the most opportunities? | Location Intelligence |
| What experience level is most sought after? | Experience Intelligence |
| How do technologies compare against each other? | Technology Trends |
| What skills should I learn next? | Career Advisor |

---

## 🏗️ Architecture

```
Kaggle CSVs (3 datasets)
    ↓
ETL Pipeline (Extract → Transform → Validate → Load)
    ↓
PostgreSQL (7 normalized tables + indexes + views)
    ↓
Analytics Engine (6 service modules)  +  ML Model (Random Forest)
    ↓
Streamlit Dashboard (7 interactive pages, 20+ Plotly charts)
```

---

## ✨ Key Features

- **Multi-Source ETL Pipeline** — Ingests datasets (Global, India, etc.), harmonizes schemas, cleans, normalizes salaries to USD, extracts skills via 150+ keyword dictionary with domain mapping (e.g., Gen-AI, Data Science).
- **Normalized PostgreSQL Schema** — 7 tables with foreign keys, indexes, and analytical views
- **7 Interactive Dashboard Modules** — Executive overview, skill/salary/location/experience intelligence, tech trends, career advisor
- **Enterprise UI Polish** — Clean dark mode aesthetic featuring the 'Inter' font, tabular numerals, and centralized sidebar routing (no emojis or default Streamlit styling).
- **20+ Plotly Visualizations** — Bar charts, heatmaps, specialized domain treemaps, box plots, scatter plots, donut charts
- **ML Salary Prediction with 5-Fold CV** — Random Forest model with interpretable binary skill features, validated using 5-Fold Cross Validation with transparent metrics (R², MAE, RMSE) displayed in the UI.
- **Rule-Based Career Advisor** — Skill gap analysis comparing user profile against market demand
- **India-Specific Filters** — Toggle to focus on Indian market insights, backed by fully mapped localized datasets.
- **Docker Deployment** — One-command setup with Docker Compose

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Database | PostgreSQL 16 |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| Frontend | Streamlit |
| Machine Learning | Scikit-learn (Random Forest) |
| Validation | Pydantic |
| ORM/DB | SQLAlchemy |
| Deployment | Docker, Docker Compose |
| Target Cloud | Render |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/tech-talent-intelligence-platform.git
cd tech-talent-intelligence-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start PostgreSQL

```bash
docker-compose up -d db
```

### 3. Initialize Database

```bash
python scripts/setup_database.py
```

### 4. Download Datasets

Download CSV files from Kaggle and place them in `data/raw/`:
- [India Tech Jobs 2024-26](https://www.kaggle.com/) → `data/raw/india_tech_jobs.csv`
- [Global AI Job Market 2025](https://www.kaggle.com/) → `data/raw/global_ai_jobs.csv`
- [SE Jobs & Salaries 2024](https://www.kaggle.com/) → `data/raw/se_salaries.csv`

### 5. Run ETL Pipeline

```bash
python scripts/run_etl.py
```

### 6. Train ML Model (Optional)

```bash
python scripts/train_model.py
```

### 7. Launch Dashboard

```bash
streamlit run app/main.py
```

Open http://localhost:8501 in your browser.

---

## 🐳 Docker (Full Stack)

```bash
# Start everything (PostgreSQL + Streamlit)
docker-compose up --build

# Initialize database and run ETL
docker-compose exec app python scripts/setup_database.py
docker-compose exec app python scripts/run_etl.py
```

---

## 📁 Project Structure

```
├── config/          # Settings, logging configuration
├── data/            # Raw CSVs, skill dictionary, location mapping
├── database/        # Schema, connection manager, SQL queries
├── etl/             # Extract, Transform, Validate, Load modules
├── analytics/       # Business logic for each dashboard module
├── ml/              # Salary prediction model
├── app/             # Streamlit pages, components, theme
├── tests/           # Unit tests
├── scripts/         # CLI entry points
├── docs/            # Resume bullets, interview prep
└── docker-compose.yml
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📊 Dashboard Modules

| Module | Visualizations |
|---|---|
| Executive Dashboard | KPI cards, bar chart, donut chart, histogram |
| Skill Intelligence | Top skills, **Domain/Category Treemaps**, co-occurrence heatmap, scatter |
| Salary Intelligence | Distribution, by skill, by city, box plots |
| Location Intelligence | Top cities, work mode, skills by city |
| Experience Intelligence | Level distribution, salary by level, skills by level |
| Technology Trends | Tech comparison, landscape treemap, full ranking |
| Career Advisor | Skill gap analysis, salary prediction, **5-Fold CV Validation Table** |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
