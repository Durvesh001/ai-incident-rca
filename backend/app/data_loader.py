import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

def load_incidents():
    with open(DATA_DIR / "incidents.json", 'r', encoding="utf-8") as file:
        return json.load(file)

def load_runbooks():
    with open(DATA_DIR / "runbooks.json", 'r', encoding="utf-8") as file:
        return json.load(file)