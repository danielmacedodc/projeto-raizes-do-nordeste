from fastapi import APIRouter

from routers.produtos import router as produtos_router
from routers.unidades import router as unidades_router

router = APIRouter()
router.include_router(unidades_router)
router.include_router(produtos_router)

__all__ = ["router"]