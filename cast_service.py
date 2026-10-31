import urllib.parse
import pychromecast
from config import settings


def falar_no_mini(texto: str) -> None:
    browser = None
    try:
        casts, browser = pychromecast.get_listed_chromecasts(
            friendly_names=[settings.cast_name]
        )
        if not casts:
            print(f"Home Mini '{settings.cast_name}' não encontrado.")
            return

        cast = casts[0]
        cast.wait()

        url = (
            "https://translate.google.com/translate_tts"
            "?ie=UTF-8&client=tw-ob&tl=pt-BR&q="
            + urllib.parse.quote(texto)
        )
        mc = cast.media_controller
        mc.play_media(url, "audio/mp3")
        mc.block_until_active()
    except Exception as e:
        print(f"Erro ao falar no Home Mini: {e}")
    finally:
        if browser:
            pychromecast.discovery.stop_discovery(browser)