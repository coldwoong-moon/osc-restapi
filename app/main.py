from fastapi import FastAPI
from app.api.endpoints import login
from app.db.config import validate_db_config, ConfigException

app = FastAPI(title="OSC API")

app.include_router(login.router, prefix="/login", tags=["Login"])


@app.on_event("startup")
async def startup_event():
    try:
        validate_db_config()
    except ConfigException as e:
        print(f"설정 오류: {str(e)}")
        raise
