"""
CLI entry point to train the salary prediction model.

Usage:
    python scripts/train_model.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.salary_predictor import train_model


if __name__ == "__main__":
    print("Training salary prediction model...")
    metrics = train_model()
    print(f"\nDone! R² = {metrics['r2']}, MAE = ${metrics['mae']}")
