from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utc_now
from models.enums import PerfilUsuario

if TYPE_CHECKING:
    from models.fidelidade import Fidelidade
    from models.pedido import Pedido


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(default=PerfilUsuario.CLIENTE, nullable=False)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="usuario")
    fidelidade_lancamentos: Mapped[list["Fidelidade"]] = relationship(back_populates="usuario")