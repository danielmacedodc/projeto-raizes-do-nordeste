from decimal import Decimal

from sqlalchemy.orm import Session

from models import Fidelidade
from models.enums import TipoMovimentoFidelidade
from services.exceptions import RegraDeNegocioViolada

PONTOS_POR_REAL = 1


def calcular_pontos(valor_total: Decimal) -> int:
    return int(valor_total) * PONTOS_POR_REAL


def registrar_acumulo(db: Session, usuario_id: int, pedido_id: int, valor_total: Decimal) -> Fidelidade:
    lancamento = Fidelidade(
        usuario_id=usuario_id,
        pedido_id=pedido_id,
        tipo=TipoMovimentoFidelidade.ACUMULO,
        pontos=calcular_pontos(valor_total),
    )
    db.add(lancamento)
    return lancamento


def calcular_saldo(db: Session, usuario_id: int) -> int:
    lancamentos = db.query(Fidelidade).filter(Fidelidade.usuario_id == usuario_id).all()
    saldo = 0
    for lancamento in lancamentos:
        if lancamento.tipo == TipoMovimentoFidelidade.ACUMULO:
            saldo += lancamento.pontos
        else:
            saldo -= lancamento.pontos
    return saldo


def resgatar_pontos(db: Session, usuario_id: int, pontos: int) -> Fidelidade:
    saldo = calcular_saldo(db, usuario_id)
    if pontos > saldo:
        raise RegraDeNegocioViolada("Saldo de pontos insuficiente para o resgate")

    lancamento = Fidelidade(
        usuario_id=usuario_id,
        pedido_id=None,
        tipo=TipoMovimentoFidelidade.RESGATE,
        pontos=pontos,
    )
    db.add(lancamento)
    db.commit()
    db.refresh(lancamento)
    return lancamento