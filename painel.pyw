import os
from pathlib import Path

PASTA = Path(__file__).resolve().parent
os.chdir(PASTA)  # garante que acha o .env mesmo abrindo por atalho

import json
import re
import socket
import subprocess
import sys
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from commands import ARQUIVO_APPS, MAPA_COMANDOS, executar_acao, ler_apps
from config import settings

ARQUIVO_NIVEIS = PASTA / "niveis.json"
SO_NO_RODAPE = ("desligar_pc", "cancelar_desligamento")
processo = None
campos = {}

VERDE, VERDE_HOVER = "#2e9e5b", "#37b86a"
VERMELHO, VERMELHO_HOVER = "#c0392b", "#e74c3c"
CINZA, CINZA_HOVER = "#3a3f4b", "#4a5060"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ---------- arquivos ----------
def ler_niveis() -> dict:
    try:
        return json.loads(ARQUIVO_NIVEIS.read_text(encoding="utf-8"))
    except Exception:
        return {}


def gravar(arquivo: Path, dados: dict):
    arquivo.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")


def porcentagens_ok(niveis: dict) -> str:
    """Devolve uma mensagem de erro, ou '' se estiver tudo certo."""
    valores = sorted(niveis.values())
    if any(v < 5 or v > 100 for v in valores):
        return "Use números de 5 a 100 (o 0 é reservado para desligar o PC)."
    for a, b in zip(valores, valores[1:]):
        if b - a < 5:
            return f"Os números {a} e {b} estão muito perto. Deixe pelo menos 5 de diferença."
    return ""


# ---------- servidor ----------
def servidor_ligado() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", settings.port), timeout=0.5):
            return True
    except OSError:
        return False


def ligar_servidor():
    global processo
    if servidor_ligado():
        return
    # pythonw.exe não tem tela de texto e quebra o uvicorn; usa o python.exe
    python = sys.executable.lower().replace("pythonw.exe", "python.exe")
    log = open(PASTA / "servidor.log", "w", encoding="utf-8")
    processo = subprocess.Popen(
        [python, "-m", "uvicorn", "main:app",
         "--host", settings.host, "--port", str(settings.port)],
        cwd=PASTA,
        stdout=log,
        stderr=log,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def desligar_servidor():
    global processo
    if processo:
        processo.terminate()
        processo = None
    elif servidor_ligado():
        messagebox.showinfo(
            "Aviso",
            "O servidor foi ligado por outro método (VS Code ou inicialização). "
            "Feche por lá.",
        )


def atualizar_status():
    global processo
    if processo and processo.poll() is not None:
        processo = None
        try:
            fim = (PASTA / "servidor.log").read_text(encoding="utf-8")[-800:]
        except Exception:
            fim = "(sem log)"
        messagebox.showerror("O servidor caiu", fim)
    if servidor_ligado():
        status.configure(text="●  Servidor ligado", text_color="#3ddc84")
    else:
        status.configure(text="●  Servidor desligado", text_color="#ff5c5c")
    janela.after(1500, atualizar_status)


# ---------- comandos ----------
def rodar_comando(comando: str):
    def tarefa():
        r = executar_acao(comando)
        if r["status"] == "erro":
            messagebox.showerror("Erro", r["mensagem"])
    threading.Thread(target=tarefa, daemon=True).start()


# ---------- lista de programas ----------
def montar_lista():
    for w in lista.winfo_children():
        w.destroy()
    campos.clear()
    niveis = ler_niveis()

    itens = [
        (c, c.replace("abrir_", "").replace("_", " ").title(), False)
        for c in MAPA_COMANDOS if c not in SO_NO_RODAPE
    ] + [(c, d["nome"], True) for c, d in ler_apps().items()]

    for comando, nome, adicionado in itens:
        card = ctk.CTkFrame(lista, corner_radius=10)
        card.pack(fill="x", pady=3, padx=2)

        ctk.CTkButton(
            card, text=nome, anchor="w", height=36,
            command=lambda c=comando: rodar_comando(c),
        ).pack(side="left", fill="x", expand=True, padx=(8, 6), pady=6)

        campo = ctk.CTkEntry(card, width=58, height=36, justify="center",
                             placeholder_text="%")
        campo.insert(0, str(niveis.get(comando, "")))
        campo.pack(side="left", padx=(0, 8 if not adicionado else 6), pady=6)
        campos[comando] = campo

        if adicionado:
            ctk.CTkButton(
                card, text="✕", width=36, height=36,
                fg_color=CINZA, hover_color=VERMELHO,
                command=lambda c=comando: remover_app(c),
            ).pack(side="left", padx=(0, 8), pady=6)


def salvar_niveis():
    novos = {}
    for comando, campo in campos.items():
        try:
            novos[comando] = int(campo.get())
        except ValueError:
            messagebox.showerror("Erro", f"Número inválido em: {comando}")
            return
    erro = porcentagens_ok(novos)
    if erro:
        messagebox.showerror("Erro", erro)
        return
    gravar(ARQUIVO_NIVEIS, novos)
    messagebox.showinfo("Salvo", "Porcentagens salvas. Já valem para a voz.")


def remover_app(comando: str):
    apps = ler_apps()
    nome = apps.get(comando, {}).get("nome", comando)
    if not messagebox.askyesno("Remover", f"Remover '{nome}' da lista?"):
        return
    apps.pop(comando, None)
    gravar(ARQUIVO_APPS, apps)
    niveis = ler_niveis()
    niveis.pop(comando, None)
    gravar(ARQUIVO_NIVEIS, niveis)
    montar_lista()


def adicionar_app():
    d = ctk.CTkToplevel(janela)
    d.title("Adicionar app")
    d.geometry("440x290")
    d.resizable(False, False)
    d.transient(janela)
    d.after(200, d.grab_set)  # espera a janela aparecer, senão dá erro no Windows

    ctk.CTkLabel(d, text="Adicionar app", font=ctk.CTkFont(size=18, weight="bold")).grid(
        row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(18, 10))

    ctk.CTkLabel(d, text="Nome").grid(row=1, column=0, sticky="w", padx=(20, 8), pady=6)
    nome = ctk.CTkEntry(d, width=220, placeholder_text="Ex: Discord")
    nome.grid(row=1, column=1, columnspan=2, sticky="w", pady=6)

    ctk.CTkLabel(d, text="Programa").grid(row=2, column=0, sticky="w", padx=(20, 8), pady=6)
    caminho = ctk.CTkEntry(d, width=220, placeholder_text="Escolha o .exe ou atalho")
    caminho.grid(row=2, column=1, sticky="w", pady=6)

    def procurar():
        c = filedialog.askopenfilename(
            parent=d, title="Escolha o programa ou atalho",
            filetypes=[("Programas e atalhos", "*.exe *.lnk *.bat"), ("Todos", "*.*")],
        )
        if c:
            caminho.delete(0, "end")
            caminho.insert(0, os.path.normpath(c))

    ctk.CTkButton(d, text="Procurar", width=80, command=procurar,
                  fg_color=CINZA, hover_color=CINZA_HOVER).grid(row=2, column=2, padx=8)

    ctk.CTkLabel(d, text="% de voz").grid(row=3, column=0, sticky="w", padx=(20, 8), pady=6)
    pct = ctk.CTkEntry(d, width=80, placeholder_text="Ex: 65")
    pct.grid(row=3, column=1, sticky="w", pady=6)

    def salvar():
        n = nome.get().strip()
        c = caminho.get().strip().strip('"')
        if not n or not c:
            messagebox.showerror("Erro", "Preencha o nome e o programa.", parent=d)
            return
        if not os.path.exists(c):
            messagebox.showerror("Erro", "Não achei esse arquivo.", parent=d)
            return
        try:
            p = int(pct.get())
        except ValueError:
            messagebox.showerror("Erro", "A porcentagem precisa ser um número.", parent=d)
            return

        chave = "app_" + re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")
        apps = ler_apps()
        if chave in apps or chave in MAPA_COMANDOS:
            messagebox.showerror("Erro", "Já existe um app com esse nome.", parent=d)
            return

        niveis = ler_niveis()
        niveis[chave] = p
        erro = porcentagens_ok(niveis)
        if erro:
            messagebox.showerror("Erro", erro, parent=d)
            return

        apps[chave] = {"nome": n, "caminho": c}
        gravar(ARQUIVO_APPS, apps)
        gravar(ARQUIVO_NIVEIS, niveis)
        montar_lista()
        d.destroy()

    ctk.CTkButton(d, text="Adicionar", height=38, command=salvar,
                  fg_color=VERDE, hover_color=VERDE_HOVER).grid(
        row=4, column=0, columnspan=3, sticky="ew", padx=20, pady=(18, 0))


def ao_fechar():
    if processo and messagebox.askyesno("Sair", "Desligar o servidor também?"):
        desligar_servidor()
    janela.destroy()


# ---------- janela ----------
janela = ctk.CTk()
janela.title("Home Mini PC")
janela.geometry("480x700")
janela.minsize(420, 520)

# topo: título + servidor
topo = ctk.CTkFrame(janela, corner_radius=12)
topo.pack(fill="x", padx=14, pady=(14, 8))
ctk.CTkLabel(topo, text="Home Mini PC", font=ctk.CTkFont(size=20, weight="bold")).pack(
    anchor="w", padx=14, pady=(10, 0))
linha_srv = ctk.CTkFrame(topo, fg_color="transparent")
linha_srv.pack(fill="x", padx=14, pady=(2, 12))
status = ctk.CTkLabel(linha_srv, text="", font=ctk.CTkFont(size=14, weight="bold"))
status.pack(side="left")
ctk.CTkButton(linha_srv, text="Desligar", width=84, command=desligar_servidor,
              fg_color=VERMELHO, hover_color=VERMELHO_HOVER).pack(side="right")
ctk.CTkButton(linha_srv, text="Ligar", width=84, command=ligar_servidor,
              fg_color=VERDE, hover_color=VERDE_HOVER).pack(side="right", padx=(0, 8))

ctk.CTkLabel(
    janela, text="Clique no programa para abrir  •  o número é a % de voz",
    text_color="gray70",
).pack(anchor="w", padx=18, pady=(4, 0))

# lista com rolagem
lista = ctk.CTkScrollableFrame(janela, fg_color="transparent")
lista.pack(fill="both", expand=True, padx=10, pady=(4, 0))

# botões da lista
botoes = ctk.CTkFrame(janela, fg_color="transparent")
botoes.pack(fill="x", padx=14, pady=8)
ctk.CTkButton(botoes, text="+ Adicionar app", height=36, command=adicionar_app,
              fg_color=CINZA, hover_color=CINZA_HOVER).pack(side="left")
ctk.CTkButton(botoes, text="Salvar porcentagens", height=36, command=salvar_niveis).pack(
    side="right")

# rodapé: desligar PC
rodape = ctk.CTkFrame(janela, corner_radius=12)
rodape.pack(fill="x", padx=14, pady=(0, 14))
ctk.CTkButton(rodape, text="Desligar PC (30s)", height=38,
              fg_color=VERMELHO, hover_color=VERMELHO_HOVER,
              command=lambda: rodar_comando("desligar_pc")).pack(
    side="left", expand=True, fill="x", padx=(10, 5), pady=10)
ctk.CTkButton(rodape, text="Cancelar", height=38,
              fg_color=CINZA, hover_color=CINZA_HOVER,
              command=lambda: rodar_comando("cancelar_desligamento")).pack(
    side="left", expand=True, fill="x", padx=(5, 10), pady=10)

janela.protocol("WM_DELETE_WINDOW", ao_fechar)
montar_lista()
ligar_servidor()  # liga sozinho ao abrir o painel
atualizar_status()
janela.mainloop()
