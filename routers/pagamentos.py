from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Pagamento, Pedido, PerfilUsuario, Usuario
from schemas.pagamento import PagamentoCreate, PagamentoRead
from services.auth import get_current_user
from services.exceptions import RegraDeNegocioViolada
from services.pagamentos import processar_pagamento

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])

DbSession = Annotated[Session, Depends(get_db)]
UsuarioAtual = Annotated[Usuario, Depends(get_current_user)]


@router.post("", response_model=PagamentoRead, status_code=status.HTTP_201_CREATED)
def criar(dados: PagamentoCreate, db: DbSession, usuario: UsuarioAtual) -> Pagamento:
    pedido = db.get(Pedido, dados.pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    if usuario.perfil == PerfilUsuario.CLIENTE and pedido.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para este recurso"
        )

    try:
        return processar_pagamento(db, dados.pedido_id, dados.metodo)
    except RegraDeNegocioViolada as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))