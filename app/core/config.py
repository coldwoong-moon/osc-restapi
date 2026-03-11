from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "RPMS REST API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "RPMS 서비스를 위한 RESTful API"

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""

    CORS_ORIGINS: list[str] = ["*"]

    FILE_STORAGE_PATH: str = "./uploads"
    FILE_CHUNK_SIZE: int = 1024 * 1024  # 1MB
    FILE_MAX_SIZE: int = 10 * 1024 * 1024 * 1024  # 10GB

    JWT_SECRET: str = "rpms-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    class Config:
        env_prefix = "RPMS_"
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
