import inspect
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__PROD_NAME__ = "OSC"
__ENV_NAME__ = f"{__PROD_NAME__}_BUILD_CONFIGURATION"


# 각 환경 변수 설정 필요
class ConfigException(Exception):
    pass


class ConfigNotFoundException(Exception):
    pass


env = os.environ.get(__ENV_NAME__, "DEV").upper()

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

    def __init__(self) -> None:
        if env != "DEV" and env != "RELEASE":
            raise ConfigException(
                f"'{env}' 환경에 해당하는 설정이 없습니다. 유효한 값: 'DEV', 'RELEASE'"
            )

        self.__set_env__()

    __env_name__ = {
        "USERNAME": f"{__PROD_NAME__}_{env}_DB_USERNAME {type(USERNAME)}",
        "PASSWORD": f"{__PROD_NAME__}_{env}_DB_PASSWORD {type(PASSWORD)}",
        "NAME": f"{__PROD_NAME__}_{env}_DB_NAME {type(NAME)}",
        "HOST": f"{__PROD_NAME__}_{env}_DB_HOST {type(HOST)}",
        "PORT": f"{__PROD_NAME__}_{env}_DB_PORT {type(PORT)}",
    }

    def __set_env__(self):
        self.USERNAME = os.environ.get(self.__env_name__.get("USERNAME").split(' ')[0])
        self.PASSWORD = os.environ.get(self.__env_name__.get("PASSWORD").split(' ')[0])
        self.NAME = os.environ.get(self.__env_name__.get("NAME").split(' ')[0])
        self.HOST = os.environ.get(self.__env_name__.get("HOST").split(' ')[0])
        self.PORT = os.environ.get(self.__env_name__.get("PORT").split(' ')[0])


config = EnvConfig()


def validate_db_config():
    try:
        empty_member_list = []

        print("[DB Environments]")
        for name, value in inspect.getmembers(config):
            if name.startswith("__") or name == "":
                continue

            if value in (0, "", None):
                print(f"add empty list : {name}, {value}")
                empty_member_list.append(f"{config.__env_name__.get(name)}")

            print(f" @ {name} : {value}")

        if len(empty_member_list):
            raise ConfigNotFoundException("다음 환경 변수의 값을 찾을 수 없습니다." + "\n - " + '\n - '.join(empty_member_list))

    except:
        raise


def get_db_connection():
    engine = create_engine(
        f"mysql+pymysql://{config.USERNAME}:{config.PASSWORD}@{config.HOST}:{config.PORT}/{config.NAME}")
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()