from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.endpoints import login
from app.db.config import validate_db_config, ConfigException

app = FastAPI()
app.title = "OSC API"
app.root_path = "/"
app.servers = [
    {"url": "/", "description": "Debug"},
    {"url": "http://develop.yteg.co.kr:8000", "description": "개발 테스트 서버(fastapi)"},
    {"url": "http://develop.yteg.co.kr:8090", "description": "개발 테스트 서버(spring boot)"},
    {"url": "https://osc.yteg.co.kr", "description": "실증 서버"},
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(login.router, prefix="/login", tags=["Login"])


@app.on_event("startup")
async def startup_event():
    try:
        validate_db_config()
    except ConfigException as e:
        print(f"설정 오류: {str(e)}")
        raise