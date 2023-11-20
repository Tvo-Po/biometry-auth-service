from typing import Protocol
from urllib import parse

from auth_service.config import settings
from .api import APIAuthDatabase
from .mongo import MongoAuthDatabase
from .sql import SQLAuthDatabase


class AuthDatabase(Protocol):
    def save_user(self, id, image: bytes): ...
    
    def get_user_face(self, id) -> bytes: ...


auth_db: AuthDatabase
url = parse.urlparse(settings.DATABASE_URL)
if url.scheme == 'mongodb':
    auth_db = MongoAuthDatabase()
elif url.scheme in {'http', 'https'}:
    auth_db = APIAuthDatabase()
else:
    auth_db = SQLAuthDatabase()
