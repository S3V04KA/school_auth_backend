import logging
import sys
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI

from app.api.routers.users import router as users_router
from app.api.routers.auth import router as auth_router
from app.api.routers.role import router as role_router
from app.config import settings
from app.database import sessionmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.log_level == "DEBUG" else logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/docs",
    redoc_url=None,
    description='Для выполнения запросов, требующих авторизацию, выполните логин и полученый токен используйте в заголовке запроса Authorization: "Bearer {token}"'
)

# app.mount("/theme", StaticFiles(directory="./app/static"), name="theme")

# @app.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html_github():
#     return get_swagger_ui_html(
#     openapi_url=app.openapi_url,
#     title=f"{app.title} - Swagger UI",
#     # swagger_ui_dark.css raw url
#     swagger_css_url="http://0.0.0.0:8000/theme/swagger-ui.css",
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(role_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
