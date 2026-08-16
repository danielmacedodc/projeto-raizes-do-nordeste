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


@router.get("/saldo", response_model=SaldoFidelidadeRead)
def obter_saldo(db: DbSession, usuario: UsuarioAtual) -> SaldoFidelidadeRead:
    saldo = calcular_saldo(db, usuario.id)
    return SaldoFidelidadeRead(usuario_id=usuario.id, saldo=saldo)


@router.post("/resgate", response_model=FidelidadeRead, status_code=status.HTTP_201_CREATED)
def resgatar(dados: FidelidadeResgate, db: DbSession, usuario: UsuarioAtual) -> Fidelidade:
    try:
        return resgatar_pontos(db, usuario.id, dados.pontos)
    except RegraDeNegocioViolada as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))