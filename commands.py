import webbrowser, datetime, time, pyautogui
from speech import speak
from nlp import *
from apps import find_best_app_match, open_app
from context import CONTEXT
from desktop_control import (
    enable_desktop_control, disable_desktop_control,
    minimize_window, maximize_window, close_window,
    show_desktop, switch_window, next_desktop, previous_desktop,
    type_text, open_folder, create_folder,
    mouse_up, mouse_down, mouse_left, mouse_right,
    mouse_click, mouse_right_click, mouse_double_click,
    mouse_scroll_up, mouse_scroll_down
)
# from nlp_engine import normalize, detect_intent
# from nlp_engine import normalize, detect_intent_with_confidence
from nlp_engine import normalize, detect_intent_with_confidence, split_steps


import os



CAMERA_ON_WORDS = ["turn on camera", "start camera", "enable camera"]
CAMERA_OFF_WORDS = ["turn off camera", "stop camera", "disable camera"]



def process_command(command):
    command = normalize_command(command)
    # commands = split_commands(command)
    steps = split_steps(command)
    


    
    # 📷 CAMERA CONTROL

    


    for cmd in steps:

        cmd = normalize(cmd)
        intent, confidence, slots = detect_intent_with_confidence(cmd)

# ---- CONFIDENCE THRESHOLDS ----
        HIGH = 0.6
        MEDIUM = 0.35

        if intent and confidence >= HIGH:
            # High confidence → act immediately
            if intent == "enable_desktop":
                speak(enable_desktop_control())
                time.sleep(0.2)
                continue

            if intent == "disable_desktop":
                speak(disable_desktop_control())
                continue

            if intent == "mouse_move":
                d = slots.get("direction")
                if d == "up": speak(mouse_up())
                elif d == "down": speak(mouse_down())
                elif d == "left": speak(mouse_left())
                elif d == "right": speak(mouse_right())
                time.sleep(0.2)
                continue

            if intent == "mouse_scroll":
                if slots.get("direction") == "up":
                    speak(mouse_scroll_up())
                elif slots.get("direction") == "down":
                    speak(mouse_scroll_down())
                    time.sleep(0.2)
                continue

            if intent == "type_text":
                speak(type_text(slots.get("text")))
                time.sleep(0.2)
                continue

        if intent and MEDIUM <= confidence < HIGH:
            # Medium confidence → ask to confirm
            speak(f"Did you mean {intent.replace('_', ' ')}?")
            continue

          # ---------- LOW CONFIDENCE ----------
        speak("I am not sure what you meant.")
        break
        



        # if intent == "enable_desktop":
        #     speak(enable_desktop_control())
        #     continue

        # if intent == "disable_desktop":
        #     speak(disable_desktop_control())
        #     continue

        # if intent == "mouse_move":
        #     direction = slots.get("direction")
        #     if direction == "up":
        #         speak(mouse_up())
        #     elif direction == "down":
        #         speak(mouse_down())
        #     elif direction == "left":
        #         speak(mouse_left())
        #     elif direction == "right":
        #         speak(mouse_right())
        #         continue

        # if intent == "mouse_scroll":
        #     if slots.get("direction") == "up":
        #         speak(mouse_scroll_up())
        #     elif slots.get("direction") == "down":
        #         speak(mouse_scroll_down())
        #         continue

        # if intent == "type_text":
        #     speak(type_text(slots.get("text")))
        #     continue



            # ---------- DESKTOP CONTROL (EXPERT MODE) ----------
        if "enable desktop control" in cmd:
            speak(enable_desktop_control())
            continue

        if "stop desktop control" in cmd or "disable desktop control" in cmd:
            speak(disable_desktop_control())
            continue

        if "minimize window" in cmd:
            minimize_window()
            continue

        if "maximize window" in cmd:
            maximize_window()
            continue

        if "close window" in cmd:
            close_window()
            continue

        if "show desktop" in cmd:
            show_desktop()
            continue

        if "switch window" in cmd or "next window" in cmd:
            switch_window()
            continue

        if "next desktop" in cmd:
            next_desktop()
            continue

        if "previous desktop" in cmd or "back desktop" in cmd:
            previous_desktop()
            continue


        # ---------- PHASE 2: VOICE FEEDBACK ACTIONS ----------

        if "type" in cmd:
            text = cmd.replace("type", "").strip()
            speak(type_text(text))
            continue

        if "open downloads" in cmd:
            speak(open_folder(os.path.join(os.path.expanduser("~"), "Downloads")))
            continue

        if "open documents" in cmd:
            speak(open_folder(os.path.join(os.path.expanduser("~"), "Documents")))
            continue

        if "create folder" in cmd:
            name = cmd.replace("create folder", "").strip()
            speak(create_folder(name))
            continue




        # ---------- PHASE 3: MOUSE CONTROL ----------
        if "mouse up" in cmd:
            speak(mouse_up())
            continue

        if "mouse down" in cmd:
            speak(mouse_down())
            continue

        if "mouse left" in cmd:
            speak(mouse_left())
            continue

        if "mouse right" in cmd:
            speak(mouse_right())
            continue

        if "click" in cmd:
            speak(mouse_click())
            continue

        if "right click" in cmd:
            speak(mouse_right_click())
            continue

        if "double click" in cmd:
            speak(mouse_double_click())
            continue

        if "scroll up" in cmd:
            speak(mouse_scroll_up())
            continue

        if "scroll down" in cmd:
            speak(mouse_scroll_down())
            continue








        if any(w in cmd for w in CAMERA_ON_WORDS):
            CONTEXT["camera_enabled"] = True
            speak("Camera enabled")
            return "OK"

        elif any(w in cmd for w in CAMERA_OFF_WORDS):
            CONTEXT["camera_enabled"] = False
            speak("Camera disabled")
            return "OK"
        
        
        action, target = extract_action_target(cmd)

        if action == "open" and target == "browser":
            webbrowser.open("https://google.com")
            speak("Opening browser")
            CONTEXT["last_target"] = "browser"

        elif action == "open" and target == "youtube":
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")
            CONTEXT["last_target"] = "youtube"

        elif action == "search":
            query = extract_parameter(cmd, "search for") or extract_parameter(cmd, "find")
            if CONTEXT["last_target"] == "youtube" and query:
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
                speak(f"Searching YouTube for {query}")
            elif CONTEXT["last_target"] == "browser" and query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                speak(f"Searching Google for {query}")
            else:
                speak("Where should I search?")

        elif action == "open":
            app_name = extract_app_name(cmd)
            if app_name:
                app_cmd = find_best_app_match(app_name)
                if app_cmd:
                    open_app(app_cmd)
                else:
                    speak(f"I couldn't find {app_name}")

        elif "time" in cmd:
            speak(datetime.datetime.now().strftime("The time is %H:%M"))

        elif "screenshot" in cmd:
            pyautogui.screenshot(f"screenshot_{int(time.time())}.png")
            speak("Screenshot saved")

        elif action == "close" and target == "assistant":
            speak("Goodbye")
            return "EXIT"

        else:
            speak("Can you rephrase that?")

    return "OK"
