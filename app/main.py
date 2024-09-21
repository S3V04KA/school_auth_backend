import logging
import sys
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI, Request, Response

from app.api.routers.users import router as users_router
from app.api.routers.auth import router as auth_router
from app.api.routers.role import router as role_router
from app.api.routers.authz import router as authz_router
from app.api.routers.traefik import router as traefik_router
from app.config import settings
from app.database import sessionmanager

from app.middlewares.auth_middleware import AuthzMiddleware
from app.middlewares.cors_middleware import CORSMiddleware

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.log_level == "DEBUG" else logging.DEBUG)


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
    root_path='/api',
    redoc_url=None,
    description='Для выполнения запросов, требующих авторизацию, выполните логин и полученый токен используйте в заголовке запроса Authorization: "Bearer {token}"'
)

app.add_middleware(CORSMiddleware)
app.add_middleware(AuthzMiddleware)

# Routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(authz_router)
app.include_router(traefik_router)

@app.get('/')
async def root(request: Request):
    response = Response(content='{"message": "Hello World"}', headers={"Content-Type": "application/json", "Access-Control-Allow-Credentials": "true"}, status_code=200)
    # response.set_cookie(key="pipa", value="1234567890", domain=request.query_params.get("domain"))
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000, log_level=logging.DEBUG)
