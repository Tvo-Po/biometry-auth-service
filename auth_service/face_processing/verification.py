from deepface import DeepFace

from auth_service.utils import byte_image_to_array


def is_faces_belong_to_same_person(given_face: bytes, original_face: bytes) -> bool:
    given_face_array = byte_image_to_array(given_face)
    original_face_array = byte_image_to_array(original_face)
    return DeepFace.verify(
        img1_path=given_face_array,
        img2_path=original_face_array,
        model_name='ArcFace',
    )['verified']
