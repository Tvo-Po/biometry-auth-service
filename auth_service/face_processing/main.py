from multiprocessing import Manager, Process, Semaphore
from multiprocessing.synchronize import Semaphore as SemaphoreType
from typing import cast

from auth_service.config import settings
from auth_service.face_processing.exception import FailedAuthError
from .data import AuthenticationResult, ProfilingRecommendation
from .profiling import identify_emotions, is_emotion_state_safe
from .verification import is_faces_belong_to_same_person


SEMAPHORE = Semaphore(settings.CONCURRENCY_LEVEL or 0)


def _parallel_verification(
    given_face: bytes,
    original_face: bytes,
    return_dict: dict,
    semaphore: SemaphoreType,
):
    semaphore.acquire()
    return_dict["verification"] = is_faces_belong_to_same_person(
        given_face,
        original_face,
    )
    semaphore.release()


def _parallel_profiling(
    given_face: bytes,
    return_dict: dict,
    semaphore: SemaphoreType,
) -> None:
    semaphore.acquire()
    emotions = identify_emotions(given_face)
    emotion_side_auth = is_emotion_state_safe(emotions)
    return_dict["profiling"] = ProfilingRecommendation(
        is_auth_recommended=emotion_side_auth,
        identified_emotions=emotions,
    )
    semaphore.release()


def _authenticate_sequential(
    given_face: bytes,
    original_face: bytes,
) -> AuthenticationResult:
    is_verificated = is_faces_belong_to_same_person(given_face, original_face)
    if not is_verificated or settings.PROFILING_STATE == "disabled":
        return AuthenticationResult(is_authenticated=is_verificated)
    emotions = identify_emotions(given_face)
    emotion_side_auth = is_emotion_state_safe(emotions)
    if settings.PROFILING_STATE == "suggesting":
        return AuthenticationResult(
            is_authenticated=True,
            recommendation=ProfilingRecommendation(
                is_auth_recommended=emotion_side_auth,
                identified_emotions=emotions,
            ),
        )
    if settings.PROFILING_STATE == "restricting":
        return AuthenticationResult(is_authenticated=emotion_side_auth)
    assert False, "Unknown profiling state."


def _authenticate_parallel(
    given_face: bytes,
    original_face: bytes,
) -> AuthenticationResult:
    with Manager() as manager:
        result_dict = manager.dict()
        verification = Process(
            target=_parallel_verification,
            args=(
                given_face,
                original_face,
                result_dict,
                SEMAPHORE,
            ),
        )
        verification.start()
        profiling = Process(
            target=_parallel_profiling,
            args=(
                given_face,
                result_dict,
                SEMAPHORE,
            ),
        )
        profiling.start()
        verification.join()
        profiling.join()
        is_verificated: bool = result_dict["verification"]  # type: ignore
        untyped_recommendation = result_dict["profiling"]  # type: ignore
        profiling_recommendation = cast(
            ProfilingRecommendation,
            untyped_recommendation,
        )
    if settings.PROFILING_STATE == "suggesting":
        return AuthenticationResult(
            is_authenticated=is_verificated,
            recommendation=profiling_recommendation,
        )
    if settings.PROFILING_STATE == "restricting":
        return AuthenticationResult(
            is_authenticated=is_verificated
            and profiling_recommendation.is_auth_recommended
        )
    assert False, "Unknown profiling state."


def verify(given_face: bytes, original_face: bytes) -> AuthenticationResult:
    result = None
    if settings.AUTH_MODE == "sequential":
        result = _authenticate_sequential(given_face, original_face)
    if settings.AUTH_MODE == "parallel":
        result = _authenticate_parallel(given_face, original_face)
    assert result is not None, "Unknown auth mode."
    if not result.is_authenticated:
        raise FailedAuthError
    return result
