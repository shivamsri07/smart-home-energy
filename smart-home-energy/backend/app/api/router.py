# backend/app/api/router.py

from fastapi import APIRouter
from ..modules.auth import endpoints as auth_endpoints
from ..modules.telemetry import endpoints as telemetry_endpoints

api_router = APIRouter()


api_router.include_router(auth_endpoints.router, prefix="/v1") # auth endpoints
api_router.include_router(telemetry_endpoints.router, prefix="/v1") # telemetry endpoints
