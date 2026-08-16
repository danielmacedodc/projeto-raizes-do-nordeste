from pydantic import BaseModel, ConfigDict, Field


class UnidadeBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    endereco: str = Field(min_length=1, max_length=255)
    cidade: str = Field(min_length=1, max_length=120)
    ativa: bool = True


class UnidadeCreate(UnidadeBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Matriz Centro",
                "endereco": "Rua das Flores, 100",
                "cidade": "Recife",
                "ativa": True,
            }
        }
    )


class UnidadeRead(UnidadeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int