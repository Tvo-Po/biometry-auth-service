from pathlib import Path

import antispoofing
from antispoofing.anti_spoof_predict import AntiSpoofPredict
from antispoofing.generate_patches import CropImage
from antispoofing.utility import parse_model_name
import numpy as np

from auth_service.utils import byte_image_to_array
from .exception import FailedValidationError


MODEL_DIR = Path(antispoofing.__file__).parent / "resources" / "anti_spoof_models"


def validate_liveness(face: bytes) -> None:
    model = AntiSpoofPredict(0)
    cropper = CropImage()
    face_array = byte_image_to_array(face)
    image_bbox = model.get_bbox(face_array)
    prediction = np.zeros((1, 3))
    for model_name in MODEL_DIR.glob("*.pth"):
        h_input, w_input, _, scale = parse_model_name(model_name.name)
        param = {
            "org_img": face_array,
            "bbox": image_bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            param["crop"] = False
        img = cropper.crop(**param)
        prediction += model.predict(img, model_name.as_posix())
    if np.argmax(prediction) != 1:
        raise FailedValidationError("Liveness detection failed")
