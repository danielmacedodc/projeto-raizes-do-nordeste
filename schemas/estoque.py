from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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