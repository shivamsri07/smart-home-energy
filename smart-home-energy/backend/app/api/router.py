# backend/app/api/router.py

from fastapi import APIRouter
from ..modules.auth import endpoints as auth_endpoints
from ..modules.telemetry.endpoints import telemetry_router, device_router
from ..modules.conversational_ai.endpoints import router as conversational_ai_router

api_router = APIRouter()


api_router.include_router(auth_endpoints.router, prefix="/v1") # auth endpoints
api_router.include_router(telemetry_router, prefix="/v1") # telemetry endpoints
api_router.include_router(device_router, prefix="/v1") # device endpoints
api_router.include_router(conversational_ai_router, prefix="/v1") # conversational ai endpoints
