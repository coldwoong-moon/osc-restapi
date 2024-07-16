import os
import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from redis import Redis

__ENV_NAME__ = "OSC_BUILD_CONFIGURATION"

# 각 환경변수 설정 필요


class ConfigException(Exception):
    pass


class Config:
    DB_USERNAME = None
    DB_PASSWORD = None
    DB_NAME = None
    DB_HOST = None
    DB_PORT = os.environ.get("OSC_DB_PORT", 3306)

    @classmethod
    def get_env(cls, key, default=None):
        value = os.environ.get(key, default)
        if value is None or value == "":
            raise ConfigException(
                f"환경 변수 '{key}'가 설정되지 않았거나 비어 있습니다."
            )
        return value


class DevelopmentConfig(Config):
    DB_USERNAME = os.environ.get("OSC_DEV_DB_USERNAME")
    DB_PASSWORD = os.environ.get("OSC_DEV_DB_PASSWORD")
    DB_HOST = os.environ.get("OSC_DEV_DB_HOST")
    DB_NAME = os.environ.get("OSC_DEV_DB_NAME")


class ProductionConfig(Config):
    DB_USERNAME = os.environ.get("OSC_RELEASE_DB_USERNAME")
    DB_PASSWORD = os.environ.get("OSC_RELEASE_DB_PASSWORD")
    DB_HOST = os.environ.get("OSC_RELEASE_DB_HOST")
    DB_NAME = os.environ.get("OSC_RELEASE_DB_NAME")


# 환경에 따른 설정 선택
env_config = {
    "dev": DevelopmentConfig,
    "release": ProductionConfig,
    "default": DevelopmentConfig,
}


def validate_db_config():
    env = os.environ.get(__ENV_NAME__, "dev")

    if env is None or env == "":
        raise ConfigException(
            f"환경 변수 '{__ENV_NAME__}'가 설정되지 않았거나 비어 있습니다."
        )

    config_class = env_config.get(env)

    if config_class is None:
        raise ConfigException(
            f"'{env}'에 해당하는 설정이 없습니다. 유효한 값: {', '.join(env_config.keys())}"
        )

    empty_member_list = []

    for name, value in inspect.getmembers(config_class):
        if name.startswith("__") or name == "":
            continue
        if value is None:
            empty_member_list.append(name)

    if empty_member_list.count(0) is not 0:
        raise ConfigException(
            f"환경 변수 '{', '.join(empty_member_list)}'를 찾을 수 없습니다."
        )


def get_mariadb_connection():
    env = os.environ.get(__ENV_NAME__, "dev")
    config = env_config.get(env)

    engine = create_engine(
        f"mysql+pymysql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def get_redis_connection():
#     Redis(host=)
