# desktop_control.py
import os
import time
import pyautogui
import keyboard
from pyautogui import FailSafeException
from context import CONTEXT

pyautogui.PAUSE = 0.05

MOUSE_STEP = 40   # small, safe movement


def _safe(action):
    try:
        action()
        return True
    except FailSafeException:
        return False


# ---------- MODE CONTROL ----------
def enable_desktop_control():
    CONTEXT["desktop_control"] = True
    return "Desktop control enabled. Proceed carefully."

def disable_desktop_control():
    CONTEXT["desktop_control"] = False
    return "Desktop control disabled."

def is_enabled():
    return CONTEXT.get("desktop_control", False)


# ---------- PHASE 1: WINDOW / DESKTOP ----------
def minimize_window():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: keyboard.send("alt+space, n"))
    return "Window minimized."

def maximize_window():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: keyboard.send("alt+space, x"))
    return "Window maximized."

def close_window():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: keyboard.send("alt+f4"))
    return "Window closed."

def show_desktop():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: keyboard.send("win+d"))
    return "Showing desktop."

def switch_window():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: keyboard.send("alt+tab"))
    return "Switching window."

def next_desktop():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: keyboard.send("ctrl+win+right"))
    return "Next desktop."

def previous_desktop():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: keyboard.send("ctrl+win+left"))
    return "Previous desktop."


# ---------- PHASE 2: KEYBOARD / FILES ----------
def type_text(text):
    if not is_enabled(): return "Desktop control is disabled."
    if not text:
        return "What should I type?"
    _safe(lambda: pyautogui.write(text, interval=0.03))
    return "Typing text."

def open_folder(path):
    if not is_enabled(): return "Desktop control is disabled."
    if os.path.exists(path):
        os.startfile(path)
        return "Opening folder."
    return "Folder not found."

def create_folder(name):
    if not is_enabled(): return "Desktop control is disabled."
    if not name:
        return "Please say a folder name."

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    path = os.path.join(desktop, name)

    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder {name} created on desktop."
    except Exception:
        return "Failed to create folder."


# ---------- PHASE 3: MOUSE CONTROL ----------
def mouse_up():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.moveRel(0, -MOUSE_STEP))
    return "Moving mouse up."

def mouse_down():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.moveRel(0, MOUSE_STEP))
    return "Moving mouse down."

def mouse_left():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.moveRel(-MOUSE_STEP, 0))
    return "Moving mouse left."

def mouse_right():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.moveRel(MOUSE_STEP, 0))
    return "Moving mouse right."

def mouse_click():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.click())
    return "Click."

def mouse_right_click():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.rightClick())
    return "Right click."

def mouse_double_click():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.doubleClick())
    return "Double click."

def mouse_scroll_up():
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.scroll(300))
    return "Scrolling up."

def mouse_scroll_down(): 
    if not is_enabled(): return "Desktop control is disabled."
    _safe(lambda: pyautogui.scroll(-300))
    return "Scrolling down."
