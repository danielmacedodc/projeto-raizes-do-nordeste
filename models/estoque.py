from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utc_now

if TYPE_CHECKING:
    from models.produto import Produto
    from models.unidade import Unidade


class Estoque(Base):
    __tablename__ = "estoques"
    __table_args__ = (
        UniqueConstraint("produto_id", "unidade_id", name="uq_estoque_produto_unidade"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    produto: Mapped["Produto"] = relationship(back_populates="estoques")
    unidade: Mapped["Unidade"] = relationship(back_populates="estoques")