from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.estoque import Estoque
    from models.item_pedido import ItemPedido


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    estoques: Mapped[list["Estoque"]] = relationship(back_populates="produto")
    itens_pedido: Mapped[list["ItemPedido"]] = relationship(back_populates="produto")