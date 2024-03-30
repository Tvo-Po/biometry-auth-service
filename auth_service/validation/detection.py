import cv2

from auth_service.utils import byte_image_to_array
from .exception import FailedValidationError


def validate_only_one_face_on_image(face: bytes) -> None:
    face_array = byte_image_to_array(face)
    gray_face = cv2.cvtColor(face_array, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(
        gray_face,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30),
    )
    if len(faces) != 1:
        raise FailedValidationError(
            f"Image must contain only one face, {len(faces)} detected"
        )
