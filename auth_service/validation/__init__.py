from pathlib import Path

from .detection import validate_only_one_face_on_image
from .liveness import validate_liveness

def validation_pipeline(image_path: Path):
    return validate_liveness(image_path)
