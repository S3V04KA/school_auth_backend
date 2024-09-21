import logging
from fastapi import APIRouter, Depends, Request, Response
from jwt import PyJWTError

from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import get_current_user
from app.crud.user import get_user_by_email
from app.schemas.auth import TokenData
from app.utils.auth import decode_jwt, get_session


router = APIRouter(
    prefix="/authz",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def authz(req: Request, db_session: DBSessionDep):
  forwarded = {
    "method": req.headers.get("x-forwarded-method"),
    "proto": req.headers.get("x-forwarded-proto"),
    "host": req.headers.get("x-forwarded-host"),
    "uri": req.headers.get("x-forwarded-uri"),
  };
  cred_response = Response(status_code=307, headers={"Location": f"{forwarded['proto']}://{forwarded['host']}{forwarded['uri'] if forwarded['uri'] else ''}"})
  cred_response.delete_cookie("token")
  cred_response.delete_cookie("token_type")
  
  try:
    user = await get_current_user(req.cookies.get("token"), db_session)
    roles = req.query_params.get('roles')
    session = await get_session(req.cookies.get("token"), db_session)
    if not session:
      return cred_response
    if roles and roles.split(',').count(user.role) != 0:
      if user.role.name.lower() in map(lambda x: x.lower(), roles.split(',')):
        return Response(status_code=200, headers={"authorization": f"{req.cookies['token_type']} {req.cookies['token']}"})
      else:
        return cred_response
  except BaseException as e:
    return cred_response
  return Response(status_code=200, headers={"authorization": f"{req.cookies['token_type']} {req.cookies['token']}"})