import cv2
import numpy as np
import requests
import os


WEB_SERVER_URL = 'http://webserver:5000/upload'


output_dir = "/app/processed"
os.makedirs(output_dir, exist_ok=True)


net = cv2.dnn.readNetFromCaffe(
    'deploy.prototxt.txt',
    'mobilenet_iter_73000.caffemodel'
)

# Deschide videoclipul
cap = cv2.VideoCapture('test.mp4')

frame_index = 0  # index pentru salvare cadru cu cadru

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    # 📌 2. Afișare dimensiuni și pixel central
    center_y, center_x = h // 2, w // 2
    print(f"[{frame_index}] Dimensiune: {w}x{h} - Pixel centru (BGR): {frame[center_y, center_x]}")

    # 📌 3. Grayscale + valoare pixel centru
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print(f"[{frame_index}] Pixel centru (grayscale): {gray[center_y, center_x]}")

    # 📌 4. Edge detection (detecție contururi)
    edges = cv2.Canny(gray, 50, 150)

    # 📌 5. Blurring
    blurred = cv2.GaussianBlur(frame, (7, 7), 0)

    # 📌 6. Desenare cerc
    circle_center = (int(w * 0.6), int(h * 0.2))
    circle_color = (26, 166, 255)  # BGR pentru #ffa61a
    cv2.circle(frame, circle_center, 40, circle_color, 3)

    # 📌 7. Detectare obiecte
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    found_object = False
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            found_object = True
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

    # 📌 8. Trimite imaginea detectată către webserver
    if found_object:
        _, img_encoded = cv2.imencode('.jpg', frame)
        try:
            requests.post(WEB_SERVER_URL, files={'image': img_encoded.tobytes()})
        except Exception as e:
            print(f"[{frame_index}] Eroare trimitere imagine:", e)

    # 📌 9. Salvează frame-ul procesat pe disc
    cv2.imwrite(os.path.join(output_dir, f"frame_{frame_index:04d}.jpg"), frame)
    frame_index += 1

cap.release()
print("Procesare video finalizată.")
