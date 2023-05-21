from pathlib import Path

import antispoofing
from antispoofing.anti_spoof_predict import AntiSpoofPredict
from antispoofing.generate_patches import CropImage
from antispoofing.utility import parse_model_name
import cv2
import numpy as np


MODEL_DIR = Path(antispoofing.__file__).parent / 'resources' / 'anti_spoof_models'


def validate_liveness(image_path: Path) -> bool:
    model = AntiSpoofPredict(0)
    cropper = CropImage()
    image = cv2.imread(image_path.as_posix())
    image_bbox = model.get_bbox(image)
    prediction = np.zeros((1, 3))
    for model_name in MODEL_DIR.glob('*.pth'):
        h_input, w_input, _, scale = parse_model_name(model_name.name)
        param = {
            "org_img": image,
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
    return np.argmax(prediction) == 1
                                                                                         