import logging
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

class CORSMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        origin = request.headers.get("Origin") if request.headers.get("Origin") else (request.headers.get("Referer") if request.headers.get("Referer") else f'{request.url.scheme}://{request.url.hostname}')
        
        if settings.domain in origin:
          response.headers["Access-Control-Allow-Origin"] = origin
          # response.headers["Access-Control-Allow-Credentials"] = "true"
          response.headers["Access-Control-Allow-Methods"] = request.method
          response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response