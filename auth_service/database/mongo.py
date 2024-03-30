from pymongo import MongoClient

from auth_service.config import settings


class MongoAuthDatabase:
    def __init__(self):
        client = MongoClient(settings.DATABASE_URL)
        self.collection = client[settings.DATABASE_NAME][
            settings.DATABASE_STRUCTURE_NAME
        ]

    def save_user(self, id, image: bytes):
        self.collection.insert_one({"id": id, "originalFaceImage": image})

    def get_user_face(self, id) -> bytes:
        return self.collection.find({"id": id})[0]["originalFaceImage"]
