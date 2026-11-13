import requests
from bs4 import BeautifulSoup
import csv
from datetime import date

url = 'https://live-tennis.eu/en/wta-live-ranking'
cabeceras = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0'}


try:
    respuesta = requests.get(url, headers=cabeceras)
    respuesta.raise_for_status()
except requests.exceptions.HTTPError as e:
    print('Error al descargar la página:', e)

# 2. Leer el HTML y buscar los nombres de las jugadoras
soup = BeautifulSoup(respuesta.content, 'lxml')
nombres = soup.find_all('td', class_='pn')
print('Jugadoras encontradas:', len(nombres))

# 3. Crear el fichero CSV con la fecha de hoy en el nombre
fichero = open('ranking_livetennis_' + str(date.today()) + '.csv', 'w', newline='', encoding='utf-8-sig')
escritor = csv.writer(fichero, delimiter=';')
escritor.writerow(['posicion', 'jugadora', 'edad', 'pais', 'puntos', 'cambio'])

# 4. Recorrer las jugadoras y guardar sus datos
for nombre in nombres:
    fila = nombre.find_parent('tr')
    celdas = fila.find_all('td')

    posicion = celdas[0].get_text(strip=True)
    jugadora = celdas[3].get_text(strip=True)
    edad = celdas[4].get_text(strip=True)
    pais = celdas[5].get_text(strip=True)
    puntos = celdas[6].get_text(strip=True)
    cambio = celdas[7].get_text(strip=True)

    escritor.writerow([posicion, jugadora, edad, pais, puntos, cambio])
    print(posicion, jugadora, pais, puntos, cambio)

fichero.close()