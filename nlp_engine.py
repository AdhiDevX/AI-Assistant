# nlp_engine.py
import re
from learning_engine import get_learned_fillers


FILLER_WORDS = [
    "please", "could you", "can you", "would you",
    "for me", "a bit", "little", "just", "hey nova",
    "nova", "kindly"
]

INTENTS = {
    "enable_desktop": ["enable desktop", "start desktop control"],
    "disable_desktop": ["stop desktop", "disable desktop control"],

    "mouse_move": ["move mouse", "mouse move"],
    "mouse_click": ["click", "press"],
    "mouse_scroll": ["scroll"],

    "open_folder": ["open folder", "open downloads", "open documents", "open desktop"],
    "type_text": ["type", "write"],

    "window_action": ["minimize", "maximize", "close window"],
}

DIRECTIONS = ["up", "down", "left", "right"]
SCROLL_DIR = ["up", "down"]

# ---------- NORMALIZATION ----------
def normalize(text: str) -> str:
    text = text.lower()
    all_fillers = FILLER_WORDS + get_learned_fillers()
    for f in all_fillers:
        text = text.replace(f, "")

    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------- INTENT DETECTION WITH CONFIDENCE ----------
def detect_intent_with_confidence(text: str):
    scores = {}

    for intent, phrases in INTENTS.items():
        score = 0
        for p in phrases:
            if p in text:
                score += len(p.split())  # longer phrase = higher confidence
        if score > 0:
            scores[intent] = score

    if not scores:
        return None, 0.0, {}

    best_intent = max(scores, key=scores.get)
    max_score = scores[best_intent]
    total = sum(scores.values())

    confidence = max_score / total if total else 0.0
    slots = extract_slots(best_intent, text)

    return best_intent, confidence, slots

# ---------- SLOT EXTRACTION ----------
def extract_slots(intent: str, text: str):
    slots = {}

    if intent == "mouse_move":
        for d in DIRECTIONS:
            if d in text:
                slots["direction"] = d

    if intent == "mouse_scroll":
        for d in SCROLL_DIR:
            if d in text:
                slots["direction"] = d

    if intent == "type_text":
        slots["text"] = (
            text.replace("type", "")
                .replace("write", "")
                .strip()
        )

    if intent == "open_folder":
        if "download" in text:
            slots["folder"] = "downloads"
        elif "document" in text:
            slots["folder"] = "documents"
        elif "desktop" in text:
            slots["folder"] = "desktop"

    return slots



# ---------- MULTI-STEP SPLITTER ----------
CONNECTORS = [" and then ", " then ", " and ", " after that "]

def split_steps(text: str):
    steps = [text]
    for c in CONNECTORS:
        new_steps = []
        for s in steps:
            if c in s:
                new_steps.extend(s.split(c))
            else:
                new_steps.append(s)
        steps = new_steps
    return [s.strip() for s in steps if s.strip()]
