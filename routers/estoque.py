from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Estoque, PerfilUsuario
from schemas.estoque import EstoqueRead, MovimentoEstoqueCreate
from services.auth import get_current_user, require_perfis
from services.estoque import registrar_movimento
from services.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada

router = APIRouter(prefix="/estoque", tags=["estoque"])

DbSession = Annotated[Session, Depends(get_db)]
RequerLogin = Depends(get_current_user)
GerenciaEstoque = Depends(
    require_perfis(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE, PerfilUsuario.COZINHA)
)


@router.post(
    "/movimentacao",
    response_model=EstoqueRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[GerenciaEstoque],
)
def movimentar(dados: MovimentoEstoqueCreate, db: DbSession) -> Estoque:
    try:
        return registrar_movimento(
            db, dados.produto_id, dados.unidade_id, dados.tipo, dados.quantidade
        )
    except RecursoNaoEncontrado as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
    except RegraDeNegocioViolada as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))


@router.get("", response_model=list[EstoqueRead], dependencies=[RequerLogin])
def listar(db: DbSession, unidade_id: int | None = None) -> list[Estoque]:
    consulta = db.query(Estoque)
    if unidade_id is not None:
        consulta = consulta.filter(Estoque.unidade_id == unidade_id)
    return consulta.all()