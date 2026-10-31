import os
import subprocess
from typing import Callable, Dict

def abrir_valorant() -> str:
    caminho = r"C:\Riot Games\Riot Client\RiotClientServices.exe"
    if os.path.exists(caminho):
        subprocess.Popen([caminho])
        return "Valorant abrindo no PC"
    os.system("start valorant:")
    return "Comando de inicialização do Valorant disparado"

def abrir_vscode() -> str:
    subprocess.Popen(["code"], shell=True)
    return "VS Code abrindo no PC"

def abrir_spotify() -> str:
    os.system("start spotify:")
    return "Spotify abrindo no PC"

MAPA_COMANDOS: Dict[str, Callable[[], str]] = {
    "abrir_valorant": abrir_valorant,
    "abrir_vscode": abrir_vscode,
    "abrir_spotify": abrir_spotify,
}

def executar_acao(comando: str) -> dict:
    handler = MAPA_COMANDOS.get(comando)
    if not handler:
        return {"status": "erro", "mensagem": f"Comando '{comando}' não reconhecido."}
    
    try:
        mensagem = handler()
        return {"status": "sucesso", "mensagem": mensagem}
    except Exception as e:
        return {"status": "erro", "mensagem": f"Falha ao executar '{comando}': {str(e)}"}
