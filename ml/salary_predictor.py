"""
Salary Predictor — Random Forest model for predicting salary based on
skills, experience, and location.

Simple, interpretable, and interview-friendly.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

from config.settings import ML_MODELS_DIR, METRO_CITIES
from config.logging_config import setup_logger
from database.connection import execute_query_df

logger = setup_logger("ml.salary_predictor")

MODEL_PATH = ML_MODELS_DIR / "salary_model.joblib"
METADATA_PATH = ML_MODELS_DIR / "salary_model_meta.joblib"

# Top skills to use as binary features (keeps model simple and interpretable)
TOP_SKILL_FEATURES = [
    "python", "java", "javascript", "sql", "react", "aws",
    "docker", "kubernetes", "typescript", "node.js",
    "angular", "go", "spring", "django", "machine learning",
    "tensorflow", "mongodb", "postgresql", "linux", "git",
]


# ===========================================================================
# Feature Engineering
# ===========================================================================

def _prepare_training_data() -> tuple:
    """
    Query database and prepare features + target for model training.

    Returns:
        (X: pd.DataFrame, y: pd.Series, feature_names: list)
    """
    query = """
        SELECT j.job_id, j.work_mode,
               el.level_name AS experience_level,
               sal.avg_salary_usd,
               l.city, l.country
        FROM jobs j
        JOIN salaries sal ON j.job_id = sal.job_id
        JOIN experience_levels el ON j.experience_level_id = el.level_id
        JOIN locations l ON j.location_id = l.location_id
        WHERE sal.avg_salary_usd IS NOT NULL
          AND sal.avg_salary_usd > 1000
          AND sal.avg_salary_usd < 500000
    """
    jobs_df = execute_query_df(query)

    if jobs_df.empty:
        raise ValueError("No salary data found in database. Run ETL first.")

    # Get skills per job
    skills_query = """
        SELECT js.job_id, sk.skill_name
        FROM job_skills js
        JOIN skills sk ON js.skill_id = sk.skill_id
    """
    skills_df = execute_query_df(skills_query)

    # Pivot skills into binary columns for each job
    job_skills = skills_df.groupby("job_id")["skill_name"].apply(set).reset_index()
    job_skills.columns = ["job_id", "skill_set"]

    # Merge
    df = jobs_df.merge(job_skills, on="job_id", how="left")
    df["skill_set"] = df["skill_set"].apply(lambda x: x if isinstance(x, set) else set())

    # --- Build features ---
    features = pd.DataFrame()

    # Experience level (ordinal encoding)
    level_order = {"Entry": 0, "Mid": 1, "Senior": 2, "Lead": 3}
    features["experience_level"] = df["experience_level"].map(level_order).fillna(0).astype(int)

    # Work mode
    work_mode_map = {"onsite": 0, "hybrid": 1, "remote": 2}
    features["work_mode"] = df["work_mode"].map(work_mode_map).fillna(0).astype(int)

    # Is metro city
    features["is_metro_city"] = df["city"].isin(METRO_CITIES).astype(int)

    # Is India
    features["is_india"] = (df["country"] == "India").astype(int)

    # Skill count
    features["skill_count"] = df["skill_set"].apply(len)

    # Binary skill features (top 20 skills)
    for skill in TOP_SKILL_FEATURES:
        features[f"has_{skill.replace(' ', '_').replace('.', '_')}"] = df["skill_set"].apply(
            lambda s: 1 if skill in s else 0
        )

    target = df["avg_salary_usd"]
    feature_names = list(features.columns)

    logger.info("Prepared %d samples with %d features", len(features), len(feature_names))
    return features, target, feature_names


# ===========================================================================
# Training
# ===========================================================================

def train_model() -> dict:
    """
    Train the salary prediction model with 5-fold cross-validation.

    Returns:
        dict with evaluation metrics including per-fold CV results.
    """
    from sklearn.model_selection import KFold, cross_validate

    logger.info("=" * 60)
    logger.info("Training Salary Prediction Model")
    logger.info("=" * 60)

    # Prepare data
    X, y, feature_names = _prepare_training_data()

    # Train/test split (hold-out set for final evaluation)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info("Train: %d samples, Test: %d samples", len(X_train), len(X_test))

    # Train Random Forest
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    logger.info("Model trained successfully")

    # Hold-out test evaluation
    y_pred = model.predict(X_test)
    metrics = {
        "mae": round(mean_absolute_error(y_test, y_pred), 2),
        "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        "r2": round(r2_score(y_test, y_pred), 4),
        "train_size": len(X_train),
        "test_size": len(X_test),
    }

    # ---------------------------------------------------------------
    # 5-Fold Cross-Validation (on full dataset)
    # ---------------------------------------------------------------
    logger.info("Running 5-fold cross-validation...")
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)

    cv_results = cross_validate(
        RandomForestRegressor(
            n_estimators=100, max_depth=15, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1,
        ),
        X, y, cv=kfold,
        scoring=["r2", "neg_mean_absolute_error", "neg_root_mean_squared_error"],
        return_train_score=True,
    )

    # Per-fold metrics
    cv_r2_scores = cv_results["test_r2"].tolist()
    cv_mae_scores = (-cv_results["test_neg_mean_absolute_error"]).tolist()
    cv_rmse_scores = (-cv_results["test_neg_root_mean_squared_error"]).tolist()
    cv_train_r2 = cv_results["train_r2"].tolist()

    metrics["cv_folds"] = 5
    metrics["cv_r2_scores"] = [round(s, 4) for s in cv_r2_scores]
    metrics["cv_r2_mean"] = round(np.mean(cv_r2_scores), 4)
    metrics["cv_r2_std"] = round(np.std(cv_r2_scores), 4)
    metrics["cv_mae_scores"] = [round(s, 2) for s in cv_mae_scores]
    metrics["cv_mae_mean"] = round(np.mean(cv_mae_scores), 2)
    metrics["cv_rmse_scores"] = [round(s, 2) for s in cv_rmse_scores]
    metrics["cv_rmse_mean"] = round(np.mean(cv_rmse_scores), 2)
    metrics["cv_train_r2_mean"] = round(np.mean(cv_train_r2), 4)
    # Overfitting indicator
    metrics["overfit_gap"] = round(np.mean(cv_train_r2) - np.mean(cv_r2_scores), 4)

    # Feature importance
    importance = pd.Series(model.feature_importances_, index=feature_names)
    importance = importance.sort_values(ascending=False)
    metrics["top_features"] = importance.head(10).to_dict()

    # Logging
    logger.info("Hold-out Test Results:")
    logger.info("  MAE:     $%.2f", metrics["mae"])
    logger.info("  RMSE:    $%.2f", metrics["rmse"])
    logger.info("  R2:      %.4f", metrics["r2"])

    logger.info("5-Fold Cross-Validation Results:")
    for i, (r2, mae, rmse) in enumerate(zip(cv_r2_scores, cv_mae_scores, cv_rmse_scores)):
        logger.info("  Fold %d: R2=%.4f  MAE=$%.2f  RMSE=$%.2f", i + 1, r2, mae, rmse)
    logger.info("  Mean R2:   %.4f +/- %.4f", metrics["cv_r2_mean"], metrics["cv_r2_std"])
    logger.info("  Mean MAE:  $%.2f", metrics["cv_mae_mean"])
    logger.info("  Mean RMSE: $%.2f", metrics["cv_rmse_mean"])
    logger.info("  Train R2:  %.4f (overfit gap: %.4f)", metrics["cv_train_r2_mean"], metrics["overfit_gap"])

    logger.info("Top 5 features:")
    for feat, imp in list(importance.head(5).items()):
        logger.info("  %-25s : %.4f", feat, imp)

    # Save model and metadata
    ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump({"feature_names": feature_names, "metrics": metrics}, METADATA_PATH)
    logger.info("Model saved to %s", MODEL_PATH)

    return metrics


# ===========================================================================
# Prediction
# ===========================================================================

def predict_salary(
    skills: list,
    experience_level: str = "Entry",
    work_mode: str = "onsite",
    is_metro: bool = True,
    is_india: bool = True,
) -> dict:
    """
    Predict salary for given inputs.

    Args:
        skills: List of skill names.
        experience_level: Entry/Mid/Senior/Lead.
        work_mode: remote/hybrid/onsite.
        is_metro: Whether location is a metro city.
        is_india: Whether location is in India.

    Returns:
        dict with predicted_salary, confidence_range, etc.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model not trained yet. Run: python scripts/train_model.py")

    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    feature_names = metadata["feature_names"]

    # Build feature vector
    features = {}

    level_order = {"Entry": 0, "Mid": 1, "Senior": 2, "Lead": 3}
    features["experience_level"] = level_order.get(experience_level, 0)

    work_mode_map = {"onsite": 0, "hybrid": 1, "remote": 2}
    features["work_mode"] = work_mode_map.get(work_mode, 0)

    features["is_metro_city"] = int(is_metro)
    features["is_india"] = int(is_india)
    features["skill_count"] = len(skills)

    skills_lower = set(s.lower() for s in skills)
    for skill in TOP_SKILL_FEATURES:
        col_name = f"has_{skill.replace(' ', '_').replace('.', '_')}"
        features[col_name] = 1 if skill in skills_lower else 0

    # Create DataFrame with correct column order
    X = pd.DataFrame([features])[feature_names]

    # Predict using all trees to get range
    predictions = np.array([tree.predict(X)[0] for tree in model.estimators_])
    predicted = model.predict(X)[0]

    return {
        "predicted_salary": round(predicted, 2),
        "salary_low": round(np.percentile(predictions, 10), 2),
        "salary_high": round(np.percentile(predictions, 90), 2),
        "confidence": "Medium" if len(skills) >= 3 else "Low",
    }


def get_model_metrics() -> dict:
    """Load and return saved model metrics."""
    if not METADATA_PATH.exists():
        return None
    metadata = joblib.load(METADATA_PATH)
    return metadata.get("metrics", {})


def get_feature_importance() -> pd.DataFrame:
    """Load model and return feature importances as a DataFrame."""
    if not MODEL_PATH.exists():
        return pd.DataFrame()

    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    feature_names = metadata["feature_names"]

    importance = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)

    return importance
