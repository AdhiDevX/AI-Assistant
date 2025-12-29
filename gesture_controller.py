import time
import cv2
import pyautogui
import keyboard
import pygetwindow as gw
from pyautogui import FailSafeException

# ---------- MediaPipe SAFE IMPORT ----------
try:
    import mediapipe as mp
except Exception as e:
    print("MediaPipe import failed:", e)
    mp = None


class GestureController:
    def __init__(self):
        self.last_action_time = 0
        self.COOLDOWN = 0.9

        if mp:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
        else:
            self.hands = None

    # ---------------- SAFE EXECUTOR ----------------
    def safe_action(self, action):
        try:
            action()
        except FailSafeException:
            # Mouse hit screen corner → pause gestures safely
            self.last_action_time = time.time()
            return

    # ---------------- Context Detection ----------------
    def is_video_context(self):
        try:
            win = gw.getActiveWindow()
            if not win:
                return False

            title = win.title.lower()
            video_keywords = [
                "youtube", "vlc", "media player",
                "mpv", "video", "player"
            ]

            return any(k in title for k in video_keywords)
        except:
            return False

    # ---------------- Finger Count ----------------
    def count_fingers(self, hand):
        tips = [4, 8, 12, 16, 20]
        pips = [2, 6, 10, 14, 18]
        fingers = []

        # Thumb
        fingers.append(
            hand.landmark[tips[0]].x >
            hand.landmark[pips[0]].x
        )

        # Other fingers
        for i in range(1, 5):
            fingers.append(
                hand.landmark[tips[i]].y <
                hand.landmark[pips[i]].y
            )

        return fingers.count(True)

    # ---------------- Main Entry ----------------
    def process_frame(self, frame):
        if not self.hands:
            return

        now = time.time()
        if now - self.last_action_time < self.COOLDOWN:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if not result.multi_hand_landmarks:
            return

        hand = result.multi_hand_landmarks[0]
        fingers = self.count_fingers(hand)

        video_mode = self.is_video_context()

        # ===== VIDEO MODE =====
        if video_mode:
            # ☝️ Forward
            if fingers == 1:
                self.safe_action(lambda: keyboard.send("right"))
                self.last_action_time = now

            # ✌️ Backward
            elif fingers == 2:
                self.safe_action(lambda: keyboard.send("left"))
                self.last_action_time = now

            # ✋ Play / Pause
            elif fingers == 5:
                self.safe_action(lambda: keyboard.send("play/pause media"))
                self.last_action_time = now

        # ===== FILE / PAGE MODE =====
        else:
            # ☝️ Scroll up
            if fingers == 1:
                self.safe_action(lambda: pyautogui.scroll(300))
                self.last_action_time = now

            # ✌️ Scroll down
            elif fingers == 2:
                self.safe_action(lambda: pyautogui.scroll(-300))
                self.last_action_time = now
