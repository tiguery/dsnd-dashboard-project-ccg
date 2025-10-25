# report/utils.py
from __future__ import annotations
from pathlib import Path
import pickle
from typing import Any

# Project root and model path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "assets" / "model.pkl"

def load_model(path: Path = MODEL_PATH) -> Any:
    with open(path, "rb") as f:
        return pickle.load(f)
