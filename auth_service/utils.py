import cv2
import numpy as np
from numpy.typing import NDArray


def byte_image_to_array(image: bytes) -> NDArray[np.uint8]:
    face_array = np.frombuffer(image, dtype=np.uint8)
    return cv2.imdecode(face_array, -1)
