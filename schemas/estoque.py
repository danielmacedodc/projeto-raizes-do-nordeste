from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.enums import TipoMovimentoEstoque


class EstoqueBase(BaseModel):
    produto_id: int
    unidade_id: int
    quantidade: int = Field(ge=0)


class EstoqueCreate(EstoqueBase):
    pass


class EstoqueRead(EstoqueBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    atualizado_em: datetime


class MovimentoEstoqueCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"produto_id": 1, "unidade_id": 1, "tipo": "ENTRADA", "quantidade": 50}
        }
    )

    produto_id: int
    unidade_id: int
    tipo: TipoMovimentoEstoque
    quantidade: int = Field(gt=0)