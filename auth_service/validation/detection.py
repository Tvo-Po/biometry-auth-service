from pathlib import Path
import cv2


def validate_only_one_face_on_image(image_path: Path) -> bool:
    image = cv2.imread(image_path.as_posix())
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        'haarcascade_frontalface_default.xml'
    )
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30),
    )
    return len(faces) == 1
