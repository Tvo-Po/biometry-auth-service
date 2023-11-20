from insightface.face_image_quality import SER_FIQ

from auth_service.utils import byte_image_to_array
from .exception import FailedValidationError


def validate_image_suitability(face: bytes) -> None:
    face_array = byte_image_to_array(face)
    ser_fiq = SER_FIQ(gpu=None)  # type: ignore
    aligned_face = ser_fiq.apply_mtcnn(face_array)
    if ser_fiq.get_score(aligned_face) < 0.75:  # type: ignore
        raise FailedValidationError("Low image quality for recognition")
