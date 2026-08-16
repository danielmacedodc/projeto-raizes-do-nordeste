from sqlalchemy.orm import Session

from models import Estoque, Produto, Unidade
from models.enums import TipoMovimentoEstoque
from services.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada


def obter_ou_criar_estoque(db: Session, produto_id: int, unidade_id: int) -> Estoque:
    estoque = (
        db.query(Estoque)
        .filter(Estoque.produto_id == produto_id, Estoque.unidade_id == unidade_id)
        .first()
    )
    if estoque is None:
        estoque = Estoque(produto_id=produto_id, unidade_id=unidade_id, quantidade=0)
        db.add(estoque)
    return estoque


def registrar_movimento(
    db: Session,
    produto_id: int,
    unidade_id: int,
    tipo: TipoMovimentoEstoque,
    quantidade: int,
) -> Estoque:
    if db.get(Produto, produto_id) is None:
        raise RecursoNaoEncontrado("Produto não encontrado")
    if db.get(Unidade, unidade_id) is None:
        raise RecursoNaoEncontrado("Unidade não encontrada")

    estoque = obter_ou_criar_estoque(db, produto_id, unidade_id)

    if tipo == TipoMovimentoEstoque.ENTRADA:
        estoque.quantidade += quantidade
    else:
        if estoque.quantidade < quantidade:
            raise RegraDeNegocioViolada("Estoque insuficiente para a saída solicitada")
        estoque.quantidade -= quantidade

    db.commit()
    db.refresh(estoque)
    return estoque