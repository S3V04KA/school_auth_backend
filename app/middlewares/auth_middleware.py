from functools import reduce
from fastapi import HTTPException, Response, status
from jwt import PyJWTError
import logging
import requests
from starlette.middleware.base import BaseHTTPMiddleware

from app.crud.user import get_user_by_email
from app.database import get_db_session
from app.schemas.auth import TokenData
from app.utils.auth import decode_jwt

class AuthzMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        path_name = request.url.path
        forwarded = {
          "method": request.headers.get("x-forwarded-method"),
          "proto": request.headers.get("x-forwarded-proto"),
          "host": request.headers.get("x-forwarded-host"),
          "uri": request.headers.get("x-forwarded-uri"),
          "ip": request.headers.get("x-forwarded-for"),
        };
        response = await call_next(request)
        
        url = f"{forwarded['proto']}://{forwarded['host']}{forwarded['uri'] if forwarded['uri'] else ''}"

        if 'authz' in path_name:
          params = request.query_params
          my_params = {}
          try:
            my_params = reduce(lambda a, b: {**a, **{b.split("=")[0]: b.split("=")[1]}}, forwarded["uri"].split("?")[-1].split("&"), {})
          except:
            pass
          failed_response = Response(status_code=307, headers={"Location": f"{params.get('url')}?url={url}"})
          if my_params.get('token') and my_params.get('token_type'):
            response = Response(status_code=307, headers={"authorization": f"{my_params['token_type']} {my_params['token']}", "Location": f"{url.split('?')[0]}"})
            response.set_cookie(key="token", value=my_params['token'], samesite='none', secure=True)
            response.set_cookie(key="token_type", value=my_params['token_type'], samesite='none', secure=True)
            return response
          if 'token' in request.cookies and 'token_type' in request.cookies:
            response.headers.append("authorization", f"{request.cookies['token_type']} {request.cookies['token']}")
            return response
          return failed_response
          
        
        return response