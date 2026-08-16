from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Fidelidade, Usuario
from schemas.fidelidade import FidelidadeRead, FidelidadeResgate, SaldoFidelidadeRead
from services.auth import get_current_user
from services.exceptions import RegraDeNegocioViolada
from services.fidelidade import calcular_saldo, resgatar_pontos

router = APIRouter(prefix="/fidelidade", tags=["fidelidade"])

DbSession = Annotated[Session, Depends(get_db)]
UsuarioAtual = Annotated[Usuario, Depends(get_current_user)]


@router.get(
    "/saldo", response_model=SaldoFidelidadeRead, summary="Consultar saldo de pontos"
)
def obter_saldo(db: DbSession, usuario: UsuarioAtual) -> SaldoFidelidadeRead:
    """Saldo sempre do usuário autenticado (1 ponto acumulado por real gasto em pedido entregue)."""
    saldo = calcular_saldo(db, usuario.id)
    return SaldoFidelidadeRead(usuario_id=usuario.id, saldo=saldo)


@router.post(
    "/resgate",
    response_model=FidelidadeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Resgatar pontos de fidelidade",
)
def resgatar(dados: FidelidadeResgate, db: DbSession, usuario: UsuarioAtual) -> Fidelidade:
    """409 se o saldo de pontos for insuficiente."""
    try:
        return resgatar_pontos(db, usuario.id, dados.pontos)
    except RegraDeNegocioViolada as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))