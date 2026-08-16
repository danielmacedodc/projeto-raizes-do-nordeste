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