from fastapi import APIRouter

from routers.auth import router as auth_router
from routers.estoque import router as estoque_router
from routers.pedidos import router as pedidos_router
from routers.produtos import router as produtos_router
from routers.unidades import router as unidades_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(unidades_router)
router.include_router(produtos_router)
router.include_router(estoque_router)
router.include_router(pedidos_router)

__all__ = ["router"]