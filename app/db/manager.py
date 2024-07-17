import os
import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from redis import Redis

__PROD_NAME__ = "OSC"
__ENV_NAME__ = f"{__PROD_NAME__}_BUILD_CONFIGURATION"

# 각 환경변수 설정 필요


class ConfigException(Exception):
    pass


class __ENV_CONFIG__:
    """조건에 맞는 환경 변수를 생성하는 클래스

    Raises:
        ConfigException: _description_
        ConfigException: _description_
    """

    DB_USERNAME = None
    DB_PASSWORD = None
    DB_NAME = None
    DB_HOST = None
    DB_PORT = os.environ.get(f"{__PROD_NAME__}_DB_PORT", 3306)
    SERVER_PORT = None

    def __init__(self) -> None:
        env = os.environ.get(__ENV_NAME__, "dev")

        if env is None or env == "":
            raise ConfigException(
                f"환경 변수 '{__ENV_NAME__}'가 설정되지 않았거나 비어 있습니다."
            )

        if env.lower() == "dev":
            self.set_env_dev()

        elif env.lower() == "release":
            self.set_env_release()
        else:
            raise ConfigException(
                f"'{env}'에 해당하는 설정이 없습니다. 유효한 값: 'dev', 'release'"
            )

    def set_env_release(self):
        build_config = "RELEASE"
        self.DB_USERNAME = os.environ.get(f"{__PROD_NAME__}_{build_config}_DB_USERNAME")
        self.DB_PASSWORD = os.environ.get(f"{__PROD_NAME__}_{build_config}_DB_PASSWORD")
        self.DB_HOST = os.environ.get(f"{__PROD_NAME__}_{build_config}_DB_HOST")
        self.DB_NAME = os.environ.get(f"{__PROD_NAME__}_{build_config}_DB_NAME")
        self.SERVER_PORT = os.environ.get(f"{__PROD_NAME__}_{build_config}_SERVER_PORT")

    def set_env_dev(self):
        self.DB_USERNAME = os.environ.get(f"{__PROD_NAME__}_DEV_DB_USERNAME")
        self.DB_PASSWORD = os.environ.get(f"{__PROD_NAME__}_DEV_DB_PASSWORD")
        self.DB_HOST = os.environ.get(f"{__PROD_NAME__}_DEV_DB_HOST")
        self.DB_NAME = os.environ.get(f"{__PROD_NAME__}_DEV_DB_NAME")
        self.SERVER_PORT = os.environ.get(f"{__PROD_NAME__}_DEV_SERVER_PORT")


def validate_db_config():
    config_class = __ENV_CONFIG__()
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


def get_db_connection():
    env = os.environ.get(__ENV_NAME__, "dev")
    config = __ENV_CONFIG__()

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
