from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    categoria: str = Field(min_length=1, max_length=80)
    preco: Decimal = Field(gt=0)
    ativo: bool = True


class ProdutoCreate(ProdutoBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "X-Burger",
                "descricao": "Hambúrguer, queijo, alface e tomate",
                "categoria": "Lanche",
                "preco": 19.90,
                "ativo": True,
            }
        }
    )


class ProdutoRead(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ProdutoUpdate(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"preco": 21.90, "ativo": True}})

    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    preco: Decimal | None = Field(default=None, gt=0)
    ativo: bool | None = None