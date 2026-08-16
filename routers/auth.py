from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas.auth import LoginRequest, TokenResponse
from schemas.usuario import UsuarioCreate, UsuarioRead
from services.auditoria import registrar
from services.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/cadastro",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
)
def cadastrar_usuario(dados: UsuarioCreate, db: DbSession) -> Usuario:
    """Cria o cadastro com senha em hash (Argon2) e registra o consentimento LGPD."""
    if db.query(Usuario).filter(Usuario.email == dados.email).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        perfil=dados.perfil,
        consentimento_lgpd=dados.consentimento_lgpd,
        senha_hash=hash_password(dados.senha),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse, summary="Autenticar e gerar token JWT")
def login(dados: LoginRequest, db: DbSession) -> TokenResponse:
    """Retorna um token Bearer válido por `ACCESS_TOKEN_EXPIRE_MINUTES` minutos."""
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if usuario is None or not verify_password(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos"
        )

    token = create_access_token(subject=str(usuario.id), perfil=usuario.perfil.value)
    registrar("login", usuario.id, email=usuario.email)
    return TokenResponse(access_token=token)