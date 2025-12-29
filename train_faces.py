import cv2
import numpy as np
import os

recognizer = cv2.face.LBPHFaceRecognizer_create()
faces = []
ids = []

for file in os.listdir("faces"):
    path = os.path.join("faces", file)
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    face_id = int(file.split(".")[1])
    faces.append(img)
    ids.append(face_id)

recognizer.train(faces, np.array(ids))
os.makedirs("trainer", exist_ok=True)
recognizer.save("trainer/trainer.yml")

print("✅ Face training complete")
