from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.estoque import Estoque
    from models.pedido import Pedido


class Unidade(Base):
    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)
    cidade: Mapped[str] = mapped_column(String(120), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    estoques: Mapped[list["Estoque"]] = relationship(back_populates="unidade")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="unidade")