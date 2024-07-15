from fastapi import FastAPI
from app.api.endpoints import user

app = FastAPI(title="Off Site Construction API")

app.include_router(user.router, prefix="/user", tags=["user"])

@app.get("/", tags=["123"])
async def root():
    return {"message": "Welcome to the API"}