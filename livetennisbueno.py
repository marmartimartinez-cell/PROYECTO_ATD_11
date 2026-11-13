import requests
from bs4 import BeautifulSoup
import csv
from datetime import date


def extraer_live_tennis():
    url = 'https://live-tennis.eu/en/wta-live-ranking'
    cabeceras = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0'}

    # 1. Descargar la página
    try:
        respuesta = requests.get(url, headers=cabeceras, timeout=20)
        respuesta.raise_for_status()
        print('Código de estado:', respuesta.status_code)
    except requests.exceptions.RequestException as e:
        print('Error al descargar la página:', e)
        return []

    # 2. Leer el HTML y buscar los nombres de las jugadoras
    soup = BeautifulSoup(respuesta.content, 'lxml')
    nombres = soup.find_all('td', class_='pn')
    print('Jugadoras encontradas:', len(nombres))

    # 3. Recorrer las jugadoras y guardar sus datos en una lista
    jugadoras = []
    for nombre in nombres:
        fila = nombre.find_parent('tr')
        celdas = fila.find_all('td')

        jugadoras.append({
            'ranking': celdas[0].get_text(strip=True),
            'nombre': celdas[3].get_text(strip=True),
            'edad': celdas[4].get_text(strip=True),
            'pais': celdas[5].get_text(strip=True),
            'puntos': celdas[6].get_text(strip=True),
            'cambio': celdas[7].get_text(strip=True)
        })

    return jugadoras


def guardar_csv(jugadoras):
    # 4. Guardar las jugadoras en un CSV con la fecha de hoy en el nombre
    nombre_fichero = 'ranking_livetennis_' + str(date.today()) + '.csv'
    fichero = open(nombre_fichero, 'w', newline='', encoding='utf-8-sig')
    escritor = csv.writer(fichero, delimiter=';')
    escritor.writerow(['ranking', 'nombre', 'edad', 'pais', 'puntos', 'cambio'])

    for j in jugadoras:
        escritor.writerow([j['ranking'], j['nombre'], j['edad'], j['pais'], j['puntos'], j['cambio']])

    fichero.close()
    print('Guardado en', nombre_fichero)


# Esto solo se ejecuta si lanzas este fichero directamente (py livetennis.py)
if __name__ == '__main__':
    jugadoras = extraer_live_tennis()
    for j in jugadoras[:15]:
        print(j['ranking'], j['nombre'], j['pais'], j['puntos'], j['cambio'])
    guardar_csv(jugadoras)