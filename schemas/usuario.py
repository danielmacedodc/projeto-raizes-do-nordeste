from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.enums import PerfilUsuario


class UsuarioBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    perfil: PerfilUsuario = PerfilUsuario.CLIENTE


class UsuarioCreate(UsuarioBase):
    senha: str = Field(min_length=8, max_length=100)
    consentimento_lgpd: bool


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    consentimento_lgpd: bool
    criado_em: datetime