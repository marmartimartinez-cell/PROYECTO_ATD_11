import requests
from bs4 import BeautifulSoup
import unicodedata


def normalizar_nombre(nombre):
    """Pasa el nombre a minúsculas y sin tildes ni caracteres especiales,
    para que el mismo nombre escrito en dos webs distintas coincida."""
    nombre = nombre.replace('\xa0', ' ')                 # espacios "raros" de algunas webs
    nombre = nombre.replace('ł', 'l').replace('Ł', 'L')  # la ł polaca no se quita sola
    nombre = unicodedata.normalize('NFKD', nombre)       # separa cada letra de su tilde
    nombre = ''.join(c for c in nombre if not unicodedata.combining(c))  # quita las tildes
    return nombre.lower().strip()


def extraer_live_tennis():
    url = 'https://live-tennis.eu/en/wta-live-ranking'
    cabeceras = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0'}

    # 1. Descargar la página
    try:
        respuesta = requests.get(url, headers=cabeceras, timeout=20)
        respuesta.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError('Error al descargar Live Tennis: ' + str(e)) from e

    # 2. Leer el HTML y buscar los nombres de las jugadoras
    soup = BeautifulSoup(respuesta.content, 'html.parser')
    nombres = soup.find_all('td', class_='pn')

    # 3. Recorrer las jugadoras y guardar sus datos en una lista
    jugadoras = []
    for nombre in nombres:
        fila = nombre.find_parent('tr')
        celdas = fila.find_all('td')

        if len(celdas) < 8:
            continue

        jugadoras.append({
            'ranking': celdas[0].get_text(strip=True),
            'nombre': celdas[3].get_text(strip=True),
            'nombre_normalizado': normalizar_nombre(celdas[3].get_text(strip=True)),
            'edad': celdas[4].get_text(strip=True),
            'pais': celdas[5].get_text(strip=True),
            'puntos': celdas[6].get_text(strip=True),
            'cambio': celdas[7].get_text(strip=True)
        })

    if not jugadoras:
        raise ValueError("Live Tennis no ha devuelto jugadoras. Puede haber cambiado el HTML.")
    return jugadoras
