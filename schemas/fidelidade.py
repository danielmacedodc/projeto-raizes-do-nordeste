from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.enums import TipoMovimentoFidelidade


class FidelidadeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    pedido_id: int | None
    tipo: TipoMovimentoFidelidade
    pontos: int
    criado_em: datetime


class FidelidadeResgate(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"pontos": 20}})

    pontos: int = Field(gt=0)


class SaldoFidelidadeRead(BaseModel):
    usuario_id: int
    saldo: int