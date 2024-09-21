import logging
from fastapi import APIRouter, Request
import requests


router = APIRouter(
    prefix="/traefik",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

