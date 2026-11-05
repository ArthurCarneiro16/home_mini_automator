import json
import os
import subprocess
from pathlib import Path
from typing import Callable, Dict

ARQUIVO_APPS = Path(__file__).parent / "apps.json"


def ler_apps() -> dict:
    """Apps adicionados pelo painel: {"app_discord": {"nome": ..., "caminho": ...}}.
    Lê toda vez, então app novo vale na hora, sem reiniciar o servidor."""
    try:
        return json.loads(ARQUIVO_APPS.read_text(encoding="utf-8"))
    except Exception:
        return {}


RIOT = r"D:\Riot Games\Riot Client\RiotClientServices.exe"
BRAVE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"


def abrir_valorant() -> str:
    if os.path.exists(RIOT):
        subprocess.Popen([RIOT, "--launch-product=valorant", "--launch-patchline=live"])
    else:
        os.system("start valorant:")
    return "Valorant abrindo no PC"


def abrir_league() -> str:
    if os.path.exists(RIOT):
        subprocess.Popen([RIOT, "--launch-product=league_of_legends", "--launch-patchline=live"])
    else:
        raise FileNotFoundError("Riot Client não encontrado")
    return "League of Legends abrindo no PC"


def abrir_brave() -> str:
    if os.path.exists(BRAVE):
        subprocess.Popen([BRAVE])
    else:
        subprocess.Popen("start brave", shell=True)
    return "Brave abrindo no PC"


def abrir_brave_anonimo() -> str:
    if os.path.exists(BRAVE):
        subprocess.Popen([BRAVE, "--incognito"])
    else:
        subprocess.Popen("start brave --incognito", shell=True)
    return "Brave anônimo abrindo no PC"


def abrir_vscode() -> str:
    subprocess.Popen(["code"], shell=True)
    return "VS Code abrindo no PC"


def abrir_spotify() -> str:
    os.system("start spotify:")
    return "Spotify abrindo no PC"


def abrir_steam() -> str:
    os.system("start steam:")
    return "Steam abrindo no PC"


def abrir_notepad() -> str:
    subprocess.Popen(["notepad"])
    return "Bloco de notas abrindo no PC"


def abrir_whatsapp() -> str:
    os.system("start whatsapp:")
    return "WhatsApp abrindo no PC"


def desligar_pc() -> str:
    # espera 30 segundos; dá para cancelar com cancelar_desligamento
    subprocess.Popen(["shutdown", "/s", "/t", "30"])
    return "PC desligando em 30 segundos"


def cancelar_desligamento() -> str:
    subprocess.Popen(["shutdown", "/a"])
    return "Desligamento cancelado"


MAPA_COMANDOS: Dict[str, Callable[[], str]] = {
    "abrir_valorant": abrir_valorant,
    "abrir_league": abrir_league,
    "abrir_brave": abrir_brave,
    "abrir_brave_anonimo": abrir_brave_anonimo,
    "abrir_vscode": abrir_vscode,
    "abrir_spotify": abrir_spotify,
    "abrir_steam": abrir_steam,
    "abrir_notepad": abrir_notepad,
    "abrir_whatsapp": abrir_whatsapp,
    "desligar_pc": desligar_pc,
    "cancelar_desligamento": cancelar_desligamento,
}


def executar_acao(comando: str) -> dict:
    handler = MAPA_COMANDOS.get(comando)
    if not handler:
        app = ler_apps().get(comando)
        if app:
            def handler():
                os.startfile(app["caminho"])
                return f"{app['nome']} abrindo no PC"
    if not handler:
        return {"status": "erro", "mensagem": f"Comando '{comando}' não reconhecido."}

    try:
        mensagem = handler()
        return {"status": "sucesso", "mensagem": mensagem}
    except Exception as e:
        return {"status": "erro", "mensagem": f"Falha ao executar '{comando}': {str(e)}"}
