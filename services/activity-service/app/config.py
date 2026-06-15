from pydantic_settings import BaseSettings

<<<<<<< HEAD
class Settings(BaseSettings):
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
=======

class Settings(BaseSettings):
    database_url: str = "sqlite:///./activities.db"
    user_service_url: str = "http://localhost:8001"
    game_service_url: str = "http://localhost:8002"

    # Added in Module 4 — RabbitMQ messaging
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672"

    # Added in Module 6 — M2M auth with auth-service
    # auth_service_url: str = "http://localhost:8005"
    # m2m_secret: str = "m2m-secret"

    model_config = {"env_file": ".env"}


settings = Settings()
>>>>>>> edcd48e1a2a7c6fcff9913d6467bc578de3d48c8
