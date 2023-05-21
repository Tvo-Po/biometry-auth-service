from dataclasses import asdict
from pathlib import Path
import tempfile
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request, status, UploadFile
from fastapi.responses import JSONResponse

from auth_service.face_processing.data import AuthenticationResult, IdetifiedEmotions, ProfilingRecommendation

from .database import auth_db
from .face_processing import verify
from .validation import validation_pipeline


app = FastAPI()


class FailedValidationError(Exception):
    pass


class FailedAuthError(Exception):
    pass


def authenticate(id: Any, given_face: Path):
    tmp = tempfile.NamedTemporaryFile('wb')
    tmp.write(auth_db.get_user_face(id))
    if not validation_pipeline(given_face):
        raise FailedValidationError
    result = verify(given_face, Path(tmp.name))
    if not result.is_authenticated:
        raise FailedAuthError
    return result


def register(id: Any, original_face: Path):
    if not validation_pipeline(original_face):
        raise FailedValidationError
    auth_db.save_user(id, original_face)


@app.post('/authenticate')
def authenticate_endpoint(id: int | UUID, face: UploadFile):
    tmp = tempfile.NamedTemporaryFile('wb')
    tmp.write(face.file.read())
    original_face = Path(__file__).parent.parent.parent / 'images' / 'sc_t.png'
    from .face_processing.profiling import identify_emotions
    result = authenticate(id, original_face)
    tmp.close()
    r = AuthenticationResult(
        is_authenticated=True,
        recommendation=ProfilingRecommendation(
            is_auth_recommended=True,
            identified_emotions=identify_emotions(original_face)
        ),
    )
    return asdict(r)


@app.post('/register')
def register_endpoint(id: int | UUID, face: UploadFile):
    tmp = tempfile.NamedTemporaryFile('wb')
    tmp.write(face.file.read())
    original_face = Path(tmp.name)
    register(id, original_face)
    tmp.close()
    return {'status': 'success'}


@app.exception_handler(FailedValidationError)
async def failed_validation_handler(request: Request, exc: FailedValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'status': "Face validation failed."}
    )


@app.exception_handler(FailedAuthError)
async def failed_authentication_handler(request: Request, exc: FailedAuthError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'status': "Authentication failed."}
    )
