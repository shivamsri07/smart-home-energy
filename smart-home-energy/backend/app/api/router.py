# backend/app/api/router.py

from fastapi import APIRouter
from ..modules.auth import endpoints as auth_endpoints

api_router = APIRouter()

# Include the authentication router
api_router.include_router(auth_endpoints.router, prefix="/v1")