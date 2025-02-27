from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  app_name: str = "KBC Interview"
  DATABASE_URL: str
  POSTGRES_DB: str
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  REDIS_HOST: str
  REDIS_PORT: str
  SECRET_KEY: str
  HASH_ALGORITHM: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int
  CELERY_BROKER_URL: str
  CELERY_RESULT_BACKEND: str
  REDIS_URL: str

  model_config = SettingsConfigDict(env_file='.env')

settings = Settings()