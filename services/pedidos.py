from sqlalchemy.orm import Session

from models import Estoque, ItemPedido, Pedido, Produto, Unidade, Usuario
from models.enums import StatusPedido
from schemas.pedido import PedidoCreate
from services.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada
from services.fidelidade import registrar_acumulo

# cozinha (EM_PREPARO) -> pronto -> entregue / cancelado; cancelamento permitido
# em qualquer estado não-terminal
TRANSICOES_PERMITIDAS: dict[StatusPedido, set[StatusPedido]] = {
    StatusPedido.RECEBIDO: {StatusPedido.EM_PREPARO, StatusPedido.CANCELADO},
    StatusPedido.EM_PREPARO: {StatusPedido.PRONTO, StatusPedido.CANCELADO},
    StatusPedido.PRONTO: {StatusPedido.ENTREGUE, StatusPedido.CANCELADO},
    StatusPedido.ENTREGUE: set(),
    StatusPedido.CANCELADO: set(),
}


def criar_pedido(db: Session, usuario: Usuario, dados: PedidoCreate) -> Pedido:
    unidade = db.get(Unidade, dados.unidade_id)
    if unidade is None:
        raise RecursoNaoEncontrado("Unidade não encontrada")

    pedido = Pedido(usuario_id=usuario.id, unidade_id=dados.unidade_id, canal=dados.canal)

    valor_total = 0
    for item in dados.itens:
        produto = db.get(Produto, item.produto_id)
        if produto is None:
            raise RecursoNaoEncontrado(f"Produto {item.produto_id} não encontrado")

        estoque = (
            db.query(Estoque)
            .filter(Estoque.produto_id == produto.id, Estoque.unidade_id == dados.unidade_id)
            .first()
        )
        disponivel = estoque.quantidade if estoque is not None else 0
        if disponivel < item.quantidade:
            raise RegraDeNegocioViolada(
                f"Estoque insuficiente para o produto {produto.id} na unidade {dados.unidade_id}"
            )
        estoque.quantidade -= item.quantidade

        valor_total += produto.preco * item.quantidade
        pedido.itens.append(
            ItemPedido(
                produto_id=produto.id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )

    pedido.valor_total = valor_total

    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


def atualizar_status(db: Session, pedido: Pedido, novo_status: StatusPedido) -> Pedido:
    permitidos = TRANSICOES_PERMITIDAS[pedido.status]
    if novo_status not in permitidos:
        raise RegraDeNegocioViolada(
            f"Transição de {pedido.status.value} para {novo_status.value} não é permitida"
        )

    pedido.status = novo_status

    if novo_status == StatusPedido.ENTREGUE:
        registrar_acumulo(db, pedido.usuario_id, pedido.id, pedido.valor_total)

    db.commit()
    db.refresh(pedido)
    return pedido