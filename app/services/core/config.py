from decouple import config

class Settings:
    SECRET_KEY: str = config('SECRET_KEY')
    ALGORITHM: str = config('ALGORITHM', default='HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config('ACCESS_TOKEN_EXPIRE_MINUTES', default=30, cast=int)
    DATABASE_URL: str = config('DATABASE_URL')

settings = Settings()