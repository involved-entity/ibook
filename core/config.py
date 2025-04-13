from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False

    database_url: str

    reset_password_token_secret: str
    verification_token_secret: str
    access_token_lifetime: int = 60 * 60 * 24 * 30

    upload_book_images_dir: str = "uploads"
    upload_book_images_url: str = "/uploads"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
