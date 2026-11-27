import cv2
import numpy as np

_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def extract_single_face(image_bytes):
    if not image_bytes or _detector.empty():
        return None
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = _detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    if len(faces) != 1:
        return None
    x, y, width, height = faces[0]
    margin_x, margin_y = int(width * 0.2), int(height * 0.2)
    return image[max(0, y-margin_y):min(image.shape[0], y+height+margin_y),
                 max(0, x-margin_x):min(image.shape[1], x+width+margin_x)]
