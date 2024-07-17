import os
import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

__PROD_NAME__ = "OSC"
__ENV_NAME__ = f"{__PROD_NAME__}_BUILD_CONFIGURATION"


# 각 환경 변수 설정 필요
class ConfigException(Exception):
    pass


class ConfigNotFoundException(Exception):
    pass


env = os.environ.get(__ENV_NAME__, "dev").upper()

if env is None or env == "":
    raise ConfigException(
        f"환경 변수 '{__ENV_NAME__}'가 설정되지 않았거나 비어 있습니다."
    )


class EnvConfig:
    USERNAME: str | None = ""
    PASSWORD: str | None = ""
    NAME: str | None = ""
    HOST: str | None = ""
    PORT: int | None = 0

    env_name = {
        "USERNAME": f"{__PROD_NAME__}_{env}_DB_USERNAME {type(USERNAME)}",
        "PASSWORD": f"{__PROD_NAME__}_{env}_DB_PASSWORD {type(PASSWORD)}",
        "NAME": f"{__PROD_NAME__}_{env}_DB_NAME {type(NAME)}",
        "HOST": f"{__PROD_NAME__}_{env}_DB_HOST {type(HOST)}",
        "PORT": f"{__PROD_NAME__}_{env}_DB_PORT {type(PORT)}",
    }

    class SERVER:
        HOST = None
        PORT = None

    def __init__(self) -> None:

        if env.lower() == "dev":
            self.set_env()

        elif env.lower() == "release":
            self.set_env()
        else:
            raise ConfigException(
                f"'{env}'에 해당하는 설정이 없습니다. 유효한 값: 'dev', 'release'"
            )

    def set_env(self):
        self.USERNAME = os.environ.get(f"{__PROD_NAME__}_{env}_DB_USERNAME")
        self.PASSWORD = os.environ.get(f"{__PROD_NAME__}_{env}_DB_PASSWORD")
        self.NAME = os.environ.get(f"{__PROD_NAME__}_{env}_DB_NAME")
        self.HOST = os.environ.get(f"{__PROD_NAME__}_{env}_DB_HOST")
        self.PORT = os.environ.get(f"{__PROD_NAME__}_{env}_DB_PORT")


config = EnvConfig()


def validate_db_config():
    try:
        empty_member_list = []

        for name, value in inspect.getmembers(EnvConfig):
            if name.startswith("__") or name == "":
                continue

            if value is "" or value is 0:
                empty_member_list.append(f"{EnvConfig.env_name.get(name)}")

        if 0 != empty_member_list.count:
            raise ConfigNotFoundException("다음 환경 변수의 값을 찾을 수 없습니다.\n - " + '\n - '.join(empty_member_list))

    except:
        raise


def get_db_connection():
    engine = create_engine(
        f"mysql+pymysql://{config.USERNAME}:{config.PASSWORD}@{config.HOST}:{config.PORT}/{config.NAME}")
    print(
        f"mysql+pymysql://{config.DB.USERNAME}:{config.DB.PASSWORD}@{config.DB.HOST}:{config.DB.PORT}/{config.DB.NAME}")
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# def get_redis_connection():
#     Redis(host=)
