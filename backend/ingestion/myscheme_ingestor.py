# backend/ingestion/myscheme_ingestor.py

import json
import os
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/


def load_mock_myscheme_data(state: str) -> List[Dict]:
    """
    Load mock scheme data for a given state from backend/mock_data/myscheme_<state>.json.
    This simulates an external API like myScheme or data.gov.in.
    """
    filename = f"myscheme_{state.lower()}.json"
    path = os.path.join(BASE_DIR, "mock_data", filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
