from pathlib import Path
from typing import Any

from httpx import Client

from auth_service.config import settings


class APIAuthDatabase:
    def __init__(self):
        self.client = Client(base_url=settings.DATABASE_URL)
    
    def save_user(self, id, image_path: Path):
        with open(image_path, 'rb') as image:
            self.client.post(f'{id}', files={'file': image.read()})
    
    def get_user_face(self, id: Any) -> bytes:
        return self.client.get(f'{id}').content
    
    def __del__(self):
        self.client.close()
