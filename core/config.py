from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False

    database_url: str

    reset_password_token_secret: str
    verification_token_secret: str
    access_token_lifetime: int = 60 * 60 * 24 * 30

    class Config:
        env_file = ".env"


settings = Settings()
