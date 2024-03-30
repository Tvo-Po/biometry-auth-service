from .detection import validate_only_one_face_on_image
from .liveness import validate_liveness
from .suitability import validate_image_suitability


def validation_pipeline(face: bytes) -> None:
    validate_only_one_face_on_image(face)
    validate_liveness(face)
    validate_image_suitability(face)
