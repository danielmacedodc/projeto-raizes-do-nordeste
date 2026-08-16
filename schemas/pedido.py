from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.enums import CanalPedido, StatusPedido


class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class ItemPedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    quantidade: int
    preco_unitario: Decimal


class PedidoCreate(BaseModel):
    unidade_id: int
    canal: CanalPedido
    itens: list[ItemPedidoCreate] = Field(min_length=1)


class PedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    unidade_id: int
    canal: CanalPedido
    status: StatusPedido
    valor_total: Decimal
    criado_em: datetime
    atualizado_em: datetime
    itens: list[ItemPedidoRead] = []


class PedidoStatusUpdate(BaseModel):
    status: StatusPedido