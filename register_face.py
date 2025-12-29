import cv2
import os

name = input("Enter your name: ").strip().lower()
face_id = abs(hash(name)) % 1000

cam = cv2.VideoCapture(0)
detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

os.makedirs("faces", exist_ok=True)
count = 0

while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        cv2.imwrite(
            f"faces/{name}.{face_id}.{count}.jpg",
            gray[y:y+h, x:x+w]
        )
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

    cv2.imshow("Register Face (Press ESC)", frame)

    if cv2.waitKey(1) & 0xFF == 27 or count >= 30:
        break

cam.release()
cv2.destroyAllWindows()
print("✅ Face registered")
