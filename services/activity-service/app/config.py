from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()