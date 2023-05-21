from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, Column, select, String
from sqlalchemy.exc import NoSuchModuleError
from sqlalchemy.orm import declarative_base, Session

from auth_service.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    Base = declarative_base()


    class User(Base):
        __tablename__ = settings.TABLE_NAME
        
        id = Column(settings.ID_COLUMN_TYPE, primary_key=True)
        originalFaceImage = Column(String(255))

except NoSuchModuleError:
    pass


class SQLAuthDatabase:
    def save_user(self, id, image_path: Path):
        with Session(engine) as session:
            u = User(id=id, originalFaceImage=image_path.as_posix())
            session.add(u)
            session.commit()
            
    def get_user_face(self, id: Any) -> bytes:
        with Session(engine) as session:
            stmt = select(User).filter_by(id=id)
            result = session.execute(stmt)
            u = result.scalar_one()
            with open(u.originalFaceImage, 'rb') as image:  # type: ignore
                return image.read()
