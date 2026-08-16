from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Pedido, PerfilUsuario, Usuario
from models.enums import CanalPedido, StatusPedido
from schemas.pagination import Pagina
from schemas.pedido import PedidoCreate, PedidoRead, PedidoStatusUpdate
from services.auth import get_current_user, require_perfis
from services.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada
from services.paginacao import paginar
from services.pedidos import atualizar_status, criar_pedido

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

DbSession = Annotated[Session, Depends(get_db)]
UsuarioAtual = Annotated[Usuario, Depends(get_current_user)]
GerenciaPedidos = Depends(
    require_perfis(
        PerfilUsuario.ADMIN,
        PerfilUsuario.GERENTE,
        PerfilUsuario.ATENDENTE,
        PerfilUsuario.COZINHA,
    )
)


@router.post(
    "", response_model=PedidoRead, status_code=status.HTTP_201_CREATED, summary="Criar pedido"
)
def criar(dados: PedidoCreate, db: DbSession, usuario: UsuarioAtual) -> Pedido:
    """Requer autenticação. `canalPedido` é obrigatório; 404 se unidade/produto não existir, 409 se estoque insuficiente."""
    try:
        return criar_pedido(db, usuario, dados)
    except RecursoNaoEncontrado as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
    except RegraDeNegocioViolada as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))


@router.get("", response_model=Pagina[PedidoRead], summary="Listar pedidos")
def listar(
    db: DbSession,
    usuario: UsuarioAtual,
    canal_pedido: Annotated[CanalPedido | None, Query(alias="canalPedido")] = None,
    status_pedido: Annotated[StatusPedido | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    """CLIENTE vê apenas os próprios pedidos; staff vê todos. Filtre por `canalPedido` e `status`."""
    consulta = db.query(Pedido)
    if usuario.perfil == PerfilUsuario.CLIENTE:
        consulta = consulta.filter(Pedido.usuario_id == usuario.id)
    if canal_pedido is not None:
        consulta = consulta.filter(Pedido.canal == canal_pedido)
    if status_pedido is not None:
        consulta = consulta.filter(Pedido.status == status_pedido)
    itens, total = paginar(consulta, page, limit)
    return {"items": itens, "page": page, "limit": limit, "total": total}


@router.get("/{pedido_id}", response_model=PedidoRead, summary="Consultar pedido por ID")
def obter(pedido_id: int, db: DbSession, usuario: UsuarioAtual) -> Pedido:
    """403 se um CLIENTE tentar consultar pedido de outro usuário."""
    pedido = db.get(Pedido, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    if usuario.perfil == PerfilUsuario.CLIENTE and pedido.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para este recurso"
        )
    return pedido


@router.patch(
    "/{pedido_id}/status",
    response_model=PedidoRead,
    dependencies=[GerenciaPedidos],
    summary="Atualizar status do pedido",
)
def atualizar(pedido_id: int, dados: PedidoStatusUpdate, db: DbSession) -> Pedido:
    """Restrito a staff (ADMIN/GERENTE/ATENDENTE/COZINHA). Transições: RECEBIDO -> EM_PREPARO -> PRONTO -> ENTREGUE, com CANCELADO permitido em qualquer estado não-terminal; 409 se a transição for inválida."""
    pedido = db.get(Pedido, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    try:
        return atualizar_status(db, pedido, dados.status)
    except RegraDeNegocioViolada as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))