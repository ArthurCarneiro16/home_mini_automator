import threading
import urllib.parse
import pychromecast
from config import settings

_trava = threading.Lock()
_cast = None
_browser = None


def _conectar() -> None:
    global _cast, _browser
    casts, browser = pychromecast.get_listed_chromecasts(
        friendly_names=[settings.cast_name]
    )
    if not casts:
        pychromecast.discovery.stop_discovery(browser)
        raise RuntimeError(f"Home Mini '{settings.cast_name}' não encontrado.")
    _cast = casts[0]
    _browser = browser
    _cast.wait()


def _desconectar() -> None:
    global _cast, _browser
    try:
        if _browser:
            pychromecast.discovery.stop_discovery(_browser)
    except Exception:
        pass
    _cast = None
    _browser = None


def preparar_mini() -> None:
    """Conecta no Mini antes do primeiro comando, para o primeiro ser rápido."""
    with _trava:
        try:
            if _cast is None:
                _conectar()
        except Exception as e:
            print(f"Erro ao conectar no Home Mini: {e}")
            _desconectar()


def falar_no_mini(texto: str) -> None:
    url = (
        "https://translate.google.com/translate_tts"
        "?ie=UTF-8&client=tw-ob&tl=pt-BR&q=" + urllib.parse.quote(texto)
    )
    with _trava:
        for _ in range(2):  # se a conexão caiu, tenta reconectar uma vez
            try:
                if _cast is None:
                    _conectar()
                mc = _cast.media_controller
                mc.play_media(url, "audio/mp3")
                mc.block_until_active(timeout=10)
                return
            except Exception as e:
                print(f"Erro ao falar no Home Mini: {e}")
                _desconectar()