from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, Request, status, UploadFile
from fastapi.responses import JSONResponse, Response


from .database import auth_db
from .face_processing import verify
from .face_processing.data import AuthenticationResult
from .face_processing.exception import FailedAuthError
from .validation import validation_pipeline
from .validation.exception import FailedValidationError


app = FastAPI()


def authenticate(id: Any, face: bytes):
    original_face = auth_db.get_user_face(id)
    validation_pipeline(face)
    return verify(face, original_face)


def register(id: Any, original_face: bytes) -> None:
    validation_pipeline(original_face)
    auth_db.save_user(id, original_face)


@app.exception_handler(FailedValidationError)
async def failed_validation_handler(request: Request, exc: FailedValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.message}
    )


@app.exception_handler(FailedAuthError)
async def failed_authentication_handler(request: Request, exc: FailedAuthError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': "Authentication failed."}
    )


def _get_face(face_image: UploadFile) -> bytes:
    return face_image.file.read()


@app.post('/register/{id}', responses={204: {'model': None}})
def register_endpoint(
    id: int | UUID,
    face: bytes = Depends(_get_face, use_cache=False)
):
    register(id, face)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post('/authenticate/{id}')
def authenticate_endpoint(
    id: int | UUID,
    face: bytes = Depends(_get_face, use_cache=False),
) -> AuthenticationResult:
    return authenticate(id, face)
