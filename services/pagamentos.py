import json
import random
from decimal import Decimal

from sqlalchemy.orm import Session

from config import settings
from models import Pagamento, Pedido
from models.enums import StatusPagamento, StatusPedido
from services.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada

# gateway mock: acima do limite, simula recusa por limite insuficiente (regra
# determinística e reproduzível em teste); no modo aleatório, simula uma
# taxa de aprovação de mercado
LIMITE_APROVACAO_MOCK = Decimal("500.00")
PROBABILIDADE_APROVACAO_ALEATORIA = 0.8


def _decidir_aprovacao(valor: Decimal) -> bool:
    if settings.pagamento_mock_modo == "aleatorio":
        return random.random() < PROBABILIDADE_APROVACAO_ALEATORIA
    return valor <= LIMITE_APROVACAO_MOCK


def processar_pagamento(db: Session, pedido_id: int, metodo: str) -> Pagamento:
    pedido = db.get(Pedido, pedido_id)
    if pedido is None:
        raise RecursoNaoEncontrado("Pedido não encontrado")

    pagamento_existente = db.query(Pagamento).filter(Pagamento.pedido_id == pedido_id).first()
    if pagamento_existente is not None:
        raise RegraDeNegocioViolada("Pedido já possui um pagamento registrado")

    aprovado = _decidir_aprovacao(pedido.valor_total)
    status_pagamento = StatusPagamento.APROVADO if aprovado else StatusPagamento.RECUSADO
    payload_mock = json.dumps(
        {
            "gateway": "mock",
            "modo": settings.pagamento_mock_modo,
            "decisao": status_pagamento.value,
            "motivo": (
                "aprovado pelo gateway mock"
                if aprovado
                else "recusado pelo gateway mock (limite insuficiente)"
            ),
        }
    )

    pagamento = Pagamento(
        pedido_id=pedido.id,
        valor=pedido.valor_total,
        metodo=metodo,
        status=status_pagamento,
        payload_mock=payload_mock,
    )
    db.add(pagamento)

    if aprovado and pedido.status == StatusPedido.RECEBIDO:
        pedido.status = StatusPedido.EM_PREPARO

    db.commit()
    db.refresh(pagamento)
    return pagamento