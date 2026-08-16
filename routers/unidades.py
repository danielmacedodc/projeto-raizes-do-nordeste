from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import PerfilUsuario, Unidade
from schemas import UnidadeCreate, UnidadeRead
from schemas.pagination import Pagina
from services.auth import require_perfis
from services.paginacao import paginar

router = APIRouter(prefix="/unidades", tags=["unidades"])

DbSession = Annotated[Session, Depends(get_db)]
GerenciaUnidades = Depends(require_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE))


@router.post(
    "",
    response_model=UnidadeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[GerenciaUnidades],
    summary="Criar unidade",
)
def criar_unidade(dados: UnidadeCreate, db: DbSession) -> Unidade:
    """Restrito a ADMIN e GERENTE."""
    unidade = Unidade(**dados.model_dump())
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade


@router.get("", response_model=Pagina[UnidadeRead], summary="Listar unidades")
def listar_unidades(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    """Acesso público, sem autenticação — cardápio e unidades são consultáveis por qualquer canal."""
    itens, total = paginar(db.query(Unidade), page, limit)
    return {"items": itens, "page": page, "limit": limit, "total": total}


@router.get("/{unidade_id}", response_model=UnidadeRead, summary="Consultar unidade por ID")
def obter_unidade(unidade_id: int, db: DbSession) -> Unidade:
    unidade = db.get(Unidade, unidade_id)
    if unidade is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada")
    return unidade