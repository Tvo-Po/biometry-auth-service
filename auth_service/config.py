from pathlib import Path
from typing import Literal, Type
from urllib import parse

from sqlalchemy import Integer, UUID
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    PROJECT_ROOT = Path(__file__).parent.parent
    
    PROFILING_STATE: Literal['disabled'] | \
                     Literal['suggesting'] | \
                     Literal['restricting'] = 'suggesting'
    
    AUTH_MODE: Literal['sequential'] | Literal['parallel'] = 'sequential'
    CONCURRENCY_LEVEL: int | None = None
    
    DATABASE_URL: str = 'mongodb://localhost:27017/'
    DATABASE_NAME: str = 'biometry_auth'
    DATABASE_STRUCTURE_NAME: str = 'user_biometry'
    
    TABLE_NAME: str | None = None
    ID_COLUMN_TYPE: Type[Integer] | Type[UUID] | None = None
    
    @validator('AUTH_MODE')
    def validate_profiling_enabled_in_parallel_auth(cls, mode, values):
        if mode == 'parallel' and values['PROFILING_STATE'] == 'disabled':
            raise ValueError("Profiling must be enabled in parallel auth.")
        return mode
    
    @validator('CONCURRENCY_LEVEL')
    def validate_parallel_auth_has_valid_concurrency_level(cls, level, values):
        if values['AUTH_MODE'] == 'parallel':
            if level is None:
                raise ValueError("Concurrency level must be set in parallel auth.")
            if level < 2:
                raise ValueError("Concurrency level must be not less than 2.")
        return level
    
    @validator('DATABASE_URL')
    def validate_sql_url_fields(cls, url, values):
        if not parse.urlparse(url).scheme in {'http', 'https', 'mongodb'}:
            if values['TABLE_NAME'] is None:
                raise ValueError("Table name must be set if using relational db.")
            if values['ID_COLUMN_TYPE'] is None:
                raise ValueError("ID column type must be set if using relational db.")
            if isinstance(values['ID_COLUMN_TYPE'], 'str') \
               and values['ID_COLUMN_TYPE'] in {'int', 'uuid'}:
                values['ID_COLUMN_TYPE'] = Integer if \
                    values['ID_COLUMN_TYPE'] == 'int' else UUID
        return url


settings = Settings()  # type: ignore
