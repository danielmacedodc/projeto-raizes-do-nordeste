from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import PerfilUsuario, Unidade
from schemas import UnidadeCreate, UnidadeRead
from services.auth import require_perfis

router = APIRouter(prefix="/unidades", tags=["unidades"])

DbSession = Annotated[Session, Depends(get_db)]
GerenciaUnidades = Depends(require_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE))


@router.post(
    "",
    response_model=UnidadeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[GerenciaUnidades],
)
def criar_unidade(dados: UnidadeCreate, db: DbSession) -> Unidade:
    unidade = Unidade(**dados.model_dump())
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade


@router.get("", response_model=list[UnidadeRead])
def listar_unidades(db: DbSession) -> list[Unidade]:
    return db.query(Unidade).all()


@router.get("/{unidade_id}", response_model=UnidadeRead)
def obter_unidade(unidade_id: int, db: DbSession) -> Unidade:
    unidade = db.get(Unidade, unidade_id)
    if unidade is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada")
    return unidade