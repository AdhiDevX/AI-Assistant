# learning_engine.py
import json
import os

DATA_FILE = "learning_data.json"

DEFAULT_DATA = {
    "filler_words": [],
    "intent_aliases": {}
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return DEFAULT_DATA.copy()
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def learn_filler_word(word: str):
    data = load_data()
    if word not in data["filler_words"]:
        data["filler_words"].append(word)
        save_data(data)

def get_learned_fillers():
    return load_data()["filler_words"]
