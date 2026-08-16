from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.enums import CanalPedido, StatusPedido

if TYPE_CHECKING:
    from models.item_pedido import ItemPedido
    from models.pagamento import Pagamento
    from models.unidade import Unidade
    from models.usuario import Usuario


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    canal: Mapped[CanalPedido] = mapped_column(nullable=False)
    status: Mapped[StatusPedido] = mapped_column(default=StatusPedido.RECEBIDO, nullable=False)
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="pedidos")
    unidade: Mapped["Unidade"] = relationship(back_populates="pedidos")
    itens: Mapped[list["ItemPedido"]] = relationship(back_populates="pedido")
    pagamento: Mapped["Pagamento | None"] = relationship(back_populates="pedido")