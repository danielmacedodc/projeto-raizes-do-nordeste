import logging

logger = logging.getLogger("auditoria")


def registrar(acao: str, usuario_id: int | None, **detalhes: object) -> None:
    logger.info("acao=%s usuario_id=%s detalhes=%s", acao, usuario_id, detalhes)