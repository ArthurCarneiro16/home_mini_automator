import asyncio
import json
from pathlib import Path

from sinricpro import SinricPro, SinricProDimSwitch, SinricProConfig
from config import settings
from commands import executar_acao

ARQUIVO_NIVEIS = Path(__file__).parent / "niveis.json"


def ler_niveis() -> dict:
    """Lê as porcentagens salvas (comando -> número). Lê toda vez, então
    mudar no painel vale na hora, sem reiniciar o servidor."""
    try:
        return json.loads(ARQUIVO_NIVEIS.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Não consegui ler o niveis.json: {e}")
        return {}


async def _rodar(comando: str) -> bool:
    resultado = await asyncio.to_thread(executar_acao, comando)
    if resultado["status"] == "sucesso":
        print(resultado["mensagem"])
        return True
    print(resultado["mensagem"])
    return False


def _criar_dimmer(device_id: str) -> SinricProDimSwitch:
    async def ao_mudar_nivel(*args) -> bool:
        nivel = int(args[-1])
        print(f"Nível recebido do Google: {nivel}")

        if nivel <= 0:
            return await _rodar("desligar_pc")

        for comando, numero in ler_niveis().items():
            if abs(nivel - int(numero)) <= 2:
                return await _rodar(comando)

        print("Esse número não está cadastrado")
        return False

    async def aceitar_estado(*args) -> bool:
        # "desligar o PC" chega como estado False
        if args and args[-1] is False:
            return await _rodar("desligar_pc")
        return True

    dispositivo = SinricProDimSwitch(device_id)
    if hasattr(dispositivo, "on_power_state"):
        dispositivo.on_power_state(aceitar_estado)

    registrar = getattr(dispositivo, "on_power_level", None) or getattr(
        dispositivo, "on_brightness", None
    )
    if registrar is None:
        print(
            "Não achei o método do nível. Disponíveis:",
            [n for n in dir(dispositivo) if n.startswith("on_")],
        )
    else:
        registrar(ao_mudar_nivel)
    return dispositivo


async def iniciar_sinric() -> None:
    if not settings.sinric_app_key or not settings.sinric_app_secret:
        print("Sinric não configurado: faltam as chaves no .env")
        return

    try:
        sinric = SinricPro.get_instance()
        if settings.sinric_id_pc:
            sinric.add(_criar_dimmer(settings.sinric_id_pc))

        config = SinricProConfig(
            app_key=settings.sinric_app_key,
            app_secret=settings.sinric_app_secret,
        )
        await sinric.begin(config)
        print("Sinric conectado.")
    except Exception as e:
        print(f"Erro ao conectar no Sinric: {e}")
