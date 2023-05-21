from pathlib import Path

from deepface import DeepFace


def is_faces_belong_to_same_person(given_face: Path, original_face: Path) -> bool:
    return DeepFace.verify(
        img1_path=given_face.as_posix(),
        img2_path=original_face.as_posix(),
        model_name='ArcFace',
    )['verified']
