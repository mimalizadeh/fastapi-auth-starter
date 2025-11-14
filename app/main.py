import logging
import sys

import uvicorn
from fastapi import FastAPI
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.auth import router as auth_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.log_level == "DEBUG" else logging.INFO)

app = FastAPI(title=settings.project_name, docs_url="/api/docs")


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Routers
app.include_router(users_router,prefix="/api/v1", tags=["users"])
app.include_router(auth_router,prefix="/api/v1", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)