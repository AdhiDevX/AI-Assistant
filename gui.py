import sys
import cv2
import psutil
import socket
import random
import math
import threading
import time
import os

from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame
)

import nova
from gesture_controller import GestureController
from context import CONTEXT


# ================= FACE AUTHENTICATION =================
def face_authentication_gui():
    if not os.path.exists("trainer/trainer.yml"):
        return True

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer/trainer.yml")

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(0)
    start = time.time()

    while time.time() - start < 6:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            _, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            if confidence < 60:
                cap.release()
                return True

    cap.release()
    return False


# ================= CENTER CORE =================
class JarvisCore(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(810, 720)
        self.angle = 0
        self.wave = 0

        self.stars = [
            QPointF(random.uniform(0, self.width()),
                    random.uniform(0, self.height()))
            for _ in range(120)
        ]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.angle = (self.angle + 1) % 360
        self.wave += 0.8

        for star in self.stars:
            star.setY(star.y() + 0.3)
            if star.y() > self.height():
                star.setY(0)
                star.setX(random.uniform(0, self.width()))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        center = self.rect().center()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 255, 255, 120))
        for star in self.stars:
            painter.drawEllipse(star, 1.2, 1.2)

        for i in range(12):
            radius = 90 + i * 16 + math.sin(
                math.radians(self.wave + i * 18)
            ) * 5
            pen = QPen(QColor(0, 220, 255, max(40, 180 - i * 12)))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, radius, radius)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 255, 255, 200))
        painter.drawEllipse(center, 12, 12)

        painter.setPen(QColor(0, 255, 255))
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "NOVA")


# ================= MAIN UI =================
class JarvisUI(QMainWindow):
    def __init__(self):
        super().__init__()

        if not face_authentication_gui():
            sys.exit()
        else:
            nova.speak("Authentication successful")
            time.sleep(1)
            nova.speak(self.get_greeting())

        self.setWindowTitle("NOVA AI SYSTEM")
        self.setGeometry(100, 50, 1400, 800)
        self.setStyleSheet("background-color:#020c14; color:cyan;")

        main = QWidget()
        self.setCentralWidget(main)
        layout = QHBoxLayout(main)

        # LEFT PANEL
        left = QVBoxLayout()
        layout.addLayout(left, 1)

        self.cpu = self.panel_item("CPU UTILIZATION")
        self.ram = self.panel_item("MEMORY ALLOCATION")
        self.disk = self.panel_item("STORAGE CAPACITY")
        self.temp = self.panel_item("CORE TEMPERATURE")
        self.power = self.panel_item("POWER STATUS")

        for w in [self.cpu, self.ram, self.disk, self.temp, self.power]:
            left.addWidget(w)
        left.addStretch()

        # CENTER
        center = QVBoxLayout()
        layout.addLayout(center, 3)
        center.addStretch()
        center.addWidget(JarvisCore(), alignment=Qt.AlignCenter)
        center.addStretch()

        # RIGHT PANEL
        right = QVBoxLayout()
        layout.addLayout(right, 1)

        self.time_panel = self.panel_item("TEMPORAL SYNCHRONIZATION")
        self.net = self.panel_item("NETWORK INTERFACE")
        self.camera_panel = self.create_camera_panel()

        right.addWidget(self.time_panel)
        right.addWidget(self.net)
        right.addStretch()
        right.addWidget(self.camera_panel)

        QTimer(self, timeout=self.update_stats).start(1000)

        # CAMERA
        self.cap = cv2.VideoCapture(0)
        self._camera_was_enabled = True
        self.gesture = GestureController()

        self.cam_timer = QTimer(self)
        self.cam_timer.timeout.connect(self.update_camera)
        self.cam_timer.start(30)

        threading.Thread(target=self.continuous_listener, daemon=True).start()

    # ===== CAMERA HARDWARE HELPERS =====
    def _release_camera_hardware(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def _ensure_camera_hardware(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)

    # ---------------- HELPERS ----------------
    def get_greeting(self):
        h = datetime.now().hour
        if h < 12:
            return "Good morning. Nova is online and ready."
        elif h < 18:
            return "Good afternoon. Nova is online and ready."
        else:
            return "Good evening. Nova is online and ready."

    def continuous_listener(self):
        while True:
            command = nova.listen()
            if command:
                if nova.process_command(command) == "EXIT":
                    self.close()
                    break

    def panel_item(self, title):
        frame = QFrame()
        frame.setStyleSheet("border:1px solid #005f73; padding:8px;")
        layout = QVBoxLayout(frame)
        label = QLabel(title)
        label.setFont(QFont("Arial", 10, QFont.Bold))
        value = QLabel("--")
        value.setFont(QFont("Consolas", 11))
        layout.addWidget(label)
        layout.addWidget(value)
        frame.value = value
        return frame

    def create_camera_panel(self):
        frame = QFrame()
        frame.setStyleSheet("border:1px solid #005f73; padding:6px;")
        layout = QVBoxLayout(frame)
        title = QLabel("VISUAL INPUT")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(260, 180)
        self.camera_label.setStyleSheet("border:1px solid cyan;")
        self.camera_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(self.camera_label)
        return frame

    # ---------------- UPDATERS ----------------
    def update_stats(self):
        self.cpu.value.setText(f"{psutil.cpu_percent()} %")

        ram = psutil.virtual_memory()
        self.ram.value.setText(
            f"{ram.used//(1024**3)} / {ram.total//(1024**3)} GB"
            )

        disk = psutil.disk_usage("/")
        self.disk.value.setText(
            f"{disk.used//(1024**3)} / {disk.total//(1024**3)} GB"
        )

    # 🌡️ Temperature (safe fallback)
        if hasattr(psutil, "sensors_temperatures"):
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name in temps:
                        if temps[name]:
                            self.temp.value.setText(
                                f"{temps[name][0].current} °C"
                            )
                            break
                    else:
                        self.temp.value.setText("N/A")
                else:
                    self.temp.value.setText("N/A")
            except:
                self.temp.value.setText("N/A")
        else:
            self.temp.value.setText("Not supported")

        # 🔋 Battery
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                status = "Charging" if battery.power_plugged else "Discharging"
                self.power.value.setText(
                    f"{battery.percent}% ({status})"
                )
            else:
                self.power.value.setText("No Battery")
        else:
            self.power.value.setText("Not supported")

        self.time_panel.value.setText(
            datetime.now().strftime("%H:%M:%S\n%A, %d %B %Y")
        )

        try:
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            self.net.value.setText("ONLINE")
        except:
            self.net.value.setText("OFFLINE")

    def update_camera(self):
        # ===== HARD CAMERA ON / OFF =====
        camera_enabled = CONTEXT.get("camera_enabled", True)

        if not camera_enabled and self._camera_was_enabled:
            self._release_camera_hardware()
            self._camera_was_enabled = False

        elif camera_enabled and not self._camera_was_enabled:
            self._ensure_camera_hardware()
            self._camera_was_enabled = True

        if not CONTEXT.get("camera_enabled", True):
            self.camera_label.clear()
            return

        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return


        self.gesture.process_frame(frame)

        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        img = QImage(frame.data, w, h, 3 * w, QImage.Format_RGB888)
        self.camera_label.setPixmap(
            QPixmap.fromImage(img).scaled(
                self.camera_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def closeEvent(self, e):
        self._release_camera_hardware()
        e.accept()


# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisUI()
    window.show()
    sys.exit(app.exec_())
