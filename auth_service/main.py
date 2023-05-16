from dataclasses import dataclass
from multiprocessing import Manager, Process, Semaphore
from multiprocessing.synchronize import Semaphore as SemaphoreType
from pathlib import Path

from deepface import DeepFace

from config import settings


SEMAPHORE = Semaphore(settings.CONCURRENCY_LEVEL or 0)


def is_faces_belong_to_same_person(given_face: Path, original_face: Path) -> bool:
    return DeepFace.verify(
        img1_path=given_face.as_posix(),
        img2_path=original_face.as_posix(),
        model_name='ArcFace',
    )['verified']


@dataclass(frozen=True, slots=True, kw_only=True)
class IdetifiedEmotions:
    angry: float
    disgust: float
    fear: float
    happy: float
    sad: float
    surprise: float
    neutral: float


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfilingRecommendation:
    is_auth_recommended: bool
    identified_emotions: IdetifiedEmotions


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthenticationResult:
    is_authenticated: bool
    recommendation: ProfilingRecommendation | None = None
    

def identify_emotions(given_face: Path) -> IdetifiedEmotions:
    return IdetifiedEmotions(
        **DeepFace.analyze(
            img_path=given_face.as_posix(),
            actions=('emotion',),
        )[0]['emotion']
    )


def is_emotion_state_safe(emotions: IdetifiedEmotions) -> bool:
    return (emotions.angry + emotions.disgust + emotions.fear) <= 0.75


def parallel_verification(
    given_face: Path,
    original_face: Path,
    return_dict: dict,
    semaphore: SemaphoreType,
):
    semaphore.acquire()
    return_dict['verification'] = is_faces_belong_to_same_person(given_face, original_face)
    semaphore.release()


def parallel_profiling(
    given_face: Path,
    return_dict: dict,
    semaphore: SemaphoreType,
) -> None:
    semaphore.acquire()
    emotions = identify_emotions(given_face)
    emotion_side_auth = is_emotion_state_safe(emotions)
    return_dict['profiling'] =ProfilingRecommendation(
        is_auth_recommended=emotion_side_auth,
        identified_emotions=emotions,
    )
    semaphore.release()


def authenticate(given_face: Path, original_face: Path) -> AuthenticationResult:
    if settings.AUTH_MODE == 'sequential':
        is_verificated = is_faces_belong_to_same_person(given_face, original_face)
        if not is_verificated or settings.PROFILING_STATE == 'disabled':
            return AuthenticationResult(is_authenticated=is_verificated)
        emotions = identify_emotions(given_face)
        emotion_side_auth = is_emotion_state_safe(emotions)
        if settings.PROFILING_STATE == 'suggesting':
            return AuthenticationResult(
                is_authenticated=True,
                recommendation=ProfilingRecommendation(
                    is_auth_recommended=emotion_side_auth,
                    identified_emotions=emotions,
                )
            )
        if settings.PROFILING_STATE == 'restricting':
            return AuthenticationResult(is_authenticated=emotion_side_auth)
        assert False, "Unknown profiling state."
    if settings.AUTH_MODE == 'parallel':
        with Manager() as manager:
            result_dict = manager.dict()
            verification = Process(target=parallel_verification, args=(
                given_face, original_face, result_dict, SEMAPHORE,
            ))
            verification.start()
            profiling = Process(target=parallel_profiling, args=(
                given_face, result_dict, SEMAPHORE,
            ))
            profiling.start()
            verification.join()
            profiling.join()
            is_verificated = result_dict['verification']
            profiling_recommendation = result_dict['profiling']
        if settings.PROFILING_STATE == 'suggesting':
            return AuthenticationResult(
                is_authenticated=is_verificated,
                recommendation=profiling_recommendation,
            )
        if settings.PROFILING_STATE == 'restricting':
            return AuthenticationResult(
                is_authenticated=is_verificated and 
                profiling_recommendation.is_auth_recommended
            )
        assert False, "Unknown profiling state."
    assert False, "Unknown auth mode."


if __name__ == '__main__':
    given = Path(__file__).parent.parent / 'images' / 'g.png'
    orig = Path(__file__).parent.parent / 'images' / 'or.png'
    print(authenticate(given, orig))
