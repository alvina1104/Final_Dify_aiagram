import json
import os
from pathlib import Path

STORAGE_FILE = 'conversations.json'

def load_data():
    if os.path.exists(STORAGE_FILE) and Path(STORAGE_FILE).stat().st_size > 0:
        with open(STORAGE_FILE, 'r', encoding='UTF-8', errors='ignore') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(STORAGE_FILE, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)