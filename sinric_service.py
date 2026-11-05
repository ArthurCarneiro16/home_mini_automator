import asyncio
from sinricpro import SinricPro, SinricProDimSwitch, SinricProConfig
from config import settings
from commands import executar_acao
from cast_service import falar_no_mini

# brilho -> (comando do commands.py, nome que o Mini fala se der erro)
NIVEIS_APPS = {
    10: ("abrir_valorant", "o Valorant"),
    20: ("abrir_league", "o League of Legends"),
    30: ("abrir_brave", "o Brave"),
    40: ("abrir_brave_anonimo", "o Brave anônimo"),
    50: ("abrir_vscode", "o VS Code"),
    60: ("abrir_steam", "a Steam"),
    70: ("abrir_notepad", "o bloco de notas"),
    80: ("abrir_whatsapp", "o WhatsApp"),
    90: ("abrir_spotify", "o Spotify"),
}


def _falar_sem_esperar(texto: str) -> None:
    asyncio.get_running_loop().run_in_executor(None, falar_no_mini, texto)


async def _rodar(comando: str, nome: str) -> bool:
    resultado = await asyncio.to_thread(executar_acao, comando)
    if resultado["status"] == "sucesso":
        _falar_sem_esperar("Abrindo")
        return True
    print(resultado["mensagem"])
    _falar_sem_esperar(f"Não consegui abrir {nome}")
    return False


def _criar_dimmer(device_id: str) -> SinricProDimSwitch:
    async def ao_mudar_nivel(*args) -> bool:
        nivel = int(args[-1])
        print(f"Nível recebido do Google: {nivel}")
        for numero, (comando, nome) in NIVEIS_APPS.items():
            if abs(nivel - numero) <= 4:
                return await _rodar(comando, nome)
        _falar_sem_esperar("Esse número não está cadastrado")
        return False

    async def aceitar_estado(*args) -> bool:
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