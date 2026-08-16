from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utc_now
from models.enums import StatusPagamento

if TYPE_CHECKING:
    from models.pedido import Pedido


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), unique=True, nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    metodo: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[StatusPagamento] = mapped_column(default=StatusPagamento.PENDENTE, nullable=False)
    payload_mock: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    pedido: Mapped["Pedido"] = relationship(back_populates="pagamento")