from deepface import DeepFace

from auth_service.utils import byte_image_to_array
from .data import IdetifiedEmotions


def identify_emotions(given_face: bytes) -> IdetifiedEmotions:
    given_face_array = byte_image_to_array(given_face)
    return IdetifiedEmotions(
        **DeepFace.analyze(
            img_path=given_face_array,
            actions=("emotion",),
        )[
            0
        ]["emotion"]
    )


def is_emotion_state_safe(emotions: IdetifiedEmotions) -> bool:
    return (emotions.angry + emotions.disgust + emotions.fear) >= 0.75
