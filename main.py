import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from config import settings
from commands import executar_acao, MAPA_COMANDOS
from cast_service import falar_no_mini, preparar_mini
from sinric_service import iniciar_sinric


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, preparar_mini)
    await iniciar_sinric()
    loop.run_in_executor(None, falar_no_mini, "Servidor ligado")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Home Mini PC Automator",
    description="API para orquestrar rotinas do PC disparadas pelo Google Home Mini",
    version="1.0.0",
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verificar_token(token: str = Security(api_key_header)):
    if not token or token != settings.api_secret_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso não autorizado: Token inválido ou ausente.",
        )
    return token


class ComandoPayload(BaseModel):
    comando: str


@app.get("/health")
def health_check():
    """Endpoint público para monitoramento de status da API."""
    return {"status": "online"}


@app.get("/comandos", dependencies=[Depends(verificar_token)])
def listar_comandos():
    """Lista todos os comandos cadastrados."""
    return {"comandos_disponiveis": list(MAPA_COMANDOS.keys())}


@app.post("/executar", dependencies=[Depends(verificar_token)])
def endpoint_executar(payload: ComandoPayload):
    """Executa uma ação no PC se o token estiver correto."""
    resultado = executar_acao(payload.comando)
    if resultado["status"] == "erro":
        raise HTTPException(status_code=400, detail=resultado["mensagem"])
    return resultado


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)