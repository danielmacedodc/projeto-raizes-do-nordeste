from sqlalchemy.orm import Query


def paginar(consulta: Query, page: int, limit: int) -> tuple[list, int]:
    total = consulta.count()
    itens = consulta.offset((page - 1) * limit).limit(limit).all()
    return itens, total