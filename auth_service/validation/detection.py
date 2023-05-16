from pathlib import Path
import cv2
import numpy as np


def validate_only_one_face_on_image(buffer) -> bool:
    image_array = np.asarray(buffer, dtype=np.uint8)
    image = cv2.imdecode(image_array, -1)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        'haarcascade_frontalface_default.xml'
    )
    # TODO: configure for subject domain
    # http://repo.ssau.ru/bitstream/Informacionnye-tehnologii-i-nanotehnologii/Issledovanie-tochnosti-detektirovaniya-lic-po-izobrazheniyam-v-zavisimosti-ot-rasy-i-pola-pri-pomoshi-kaskadov-Haara-84919/1/%d0%98%d0%a2%d0%9d%d0%a2-2020_%d1%82%d0%be%d0%bc%204-481-488.pdf
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30),
    )
    return len(faces) == 1


if __name__ == '__main__':
    path = Path(__file__).parent.parent.parent / 'images' / 'pbpOZZBu0q0.png'
    with open(path, 'rb') as file:
        buffer = bytearray(file.read())
    validate_only_one_face_on_image(buffer)
