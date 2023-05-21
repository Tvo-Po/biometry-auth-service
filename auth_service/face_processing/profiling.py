from pathlib import Path

from deepface import DeepFace

from .data import IdetifiedEmotions


def identify_emotions(given_face: Path) -> IdetifiedEmotions:
    return IdetifiedEmotions(
        **DeepFace.analyze(
            img_path=given_face.as_posix(),
            actions=('emotion',),
        )[0]['emotion']
    )


def is_emotion_state_safe(emotions: IdetifiedEmotions) -> bool:
    return (emotions.angry + emotions.disgust + emotions.fear) <= 0.75
                                                                                         