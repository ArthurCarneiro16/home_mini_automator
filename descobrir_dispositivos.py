
import pychromecast

print("Buscando dispositivos na rede Wi-Fi...")
chromecasts, browser = pychromecast.get_chromecasts()

if not chromecasts:
    print("Nenhum aparelho encontrado. Verifique se o PC e o Home Mini estão na mesma rede.")
else:
    for cast in chromecasts:
        print(f"Dispositivo: '{cast.name}' | Modelo: {cast.model_name}")

pychromecast.discovery.stop_discovery(browser)