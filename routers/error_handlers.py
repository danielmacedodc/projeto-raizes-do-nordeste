from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _erro_json(status_code: int, mensagem: str, detalhes: list[dict] | None = None) -> JSONResponse:
    corpo = {"erro": {"status_code": status_code, "mensagem": mensagem}}
    if detalhes is not None:
        corpo["erro"]["detalhes"] = detalhes
    return JSONResponse(status_code=status_code, content=corpo)


def registrar_handlers_de_erro(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    def tratar_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _erro_json(exc.status_code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    def tratar_erro_de_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
        detalhes = [
            {"campo": ".".join(str(parte) for parte in erro["loc"]), "mensagem": erro["msg"]}
            for erro in exc.errors()
        ]
        return _erro_json(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Erro de validação nos dados enviados", detalhes
        )

    @app.exception_handler(Exception)
    def tratar_erro_inesperado(request: Request, exc: Exception) -> JSONResponse:
        return _erro_json(status.HTTP_500_INTERNAL_SERVER_ERROR, "Erro interno inesperado")