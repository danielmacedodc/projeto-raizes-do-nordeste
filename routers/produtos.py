from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Produto
from schemas import ProdutoCreate, ProdutoRead

router = APIRouter(prefix="/produtos", tags=["produtos"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ProdutoRead, status_code=status.HTTP_201_CREATED)
def criar_produto(dados: ProdutoCreate, db: DbSession) -> Produto:
    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.get("", response_model=list[ProdutoRead])
def listar_produtos(db: DbSession) -> list[Produto]:
    return db.query(Produto).all()


@router.get("/{produto_id}", response_model=ProdutoRead)
def obter_produto(produto_id: int, db: DbSession) -> Produto:
    produto = db.get(Produto, produto_id)
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto