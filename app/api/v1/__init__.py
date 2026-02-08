from fastapi import APIRouter

from app.api.v1.order import router as order_router
from app.core import settings

api_v1_router = APIRouter(prefix=settings.api.v1.prefix)
api_v1_router.include_router(order_router, prefix=settings.api.v1.order)
