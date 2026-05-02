import pyautogui
import time

# Gesture → media key mapping
ACTION_MAP = {
    "fist":        "playpause",
    "open_palm":   "volumemute",
    "index_point": "prevtrack",
    "peace":       "nexttrack",
    "thumbs_up":   "f",
}

COOLDOWN = 1.5   # seconds between actions

last_trigger_time = 0

def trigger_action(gesture, confidence):
    global last_trigger_time

    # Ignore low confidence predictions
    if confidence < 0.6:
        return None

    # Ignore if cooldown hasn't passed
    now = time.time()
    if now - last_trigger_time < COOLDOWN:
        return None

    # Ignore unknown gestures
    if gesture not in ACTION_MAP:
        return None

    # Trigger the action
    key = ACTION_MAP[gesture]
    pyautogui.press(key)
    last_trigger_time = now

    return f"Triggered: {gesture} → {key}"