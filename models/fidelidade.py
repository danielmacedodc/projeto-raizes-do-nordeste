from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utc_now
from models.enums import TipoMovimentoFidelidade

if TYPE_CHECKING:
    from models.pedido import Pedido
    from models.usuario import Usuario


class Fidelidade(Base):
    __tablename__ = "fidelidade_lancamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    pedido_id: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id"), nullable=True)
    tipo: Mapped[TipoMovimentoFidelidade] = mapped_column(nullable=False)
    pontos: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="fidelidade_lancamentos")
    pedido: Mapped["Pedido | None"] = relationship()