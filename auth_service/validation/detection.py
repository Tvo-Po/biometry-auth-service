import io
from pathlib import Path
import cv2
import numpy as np

from exception import FaceValidationError
    

def validate_only_one_face_on_image(buffer) -> None:
    image_array = np.asarray(buffer, dtype=np.uint8)
    image = cv2.imdecode(image_array, -1)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        'haarcascade_frontalface_default.xml'
    )
    # TODO: configure for subject domain
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30),
    )
    print(len(faces))
    if len(faces) != 1:
        raise FaceValidationError(
            f"Only one face must be on input image. Found {len(faces)}."
        )


if __name__ == '__main__':
    path = Path(__file__).parent.parent.parent / 'images' / 'people.jpg'
    with open(path, 'rb') as file:
        buffer = bytearray(file.read())
    validate_only_one_face_on_image(buffer)
