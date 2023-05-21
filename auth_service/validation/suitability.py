from pathlib import Path

import numpy as np
from tensorflow import keras

from auth_service.config import settings


MODEL = keras.models.load_model(settings.PROJECT_ROOT / 'suitability_model')


def validate_image_suitability(image_path: Path) -> bool:
    image = keras.utils.img_to_array(image_path.as_posix())
    input_arr = np.array([keras.utils.img_to_array(image)])
    return bool(round(MODEL.predict(input_arr)))
                                                                                         