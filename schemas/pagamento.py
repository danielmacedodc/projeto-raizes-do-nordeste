from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.enums import StatusPagamento


class PagamentoCreate(BaseModel):
    pedido_id: int
    metodo: str = Field(min_length=1, max_length=40)


class PagamentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pedido_id: int
    valor: Decimal
    metodo: str
    status: StatusPagamento
    payload_mock: str | None
    criado_em: datetime