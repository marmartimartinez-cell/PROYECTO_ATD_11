


import requests as r
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


# FUNCIÓN 1: Aceptar cookies
def aceptar_cookies(driver):
    driver.implicitly_wait(10)

    try:
        aceptar = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        aceptar.click()

    except Exception as e:
        print("No se encontró el botón de aceptar cookies:", e)


# FUNCIÓN 2: Cerrar pop-ups
def cerrar_popup_weblayer(driver, nombre_clase_popup):

    try:
        host_elements = driver.find_elements(By.TAG_NAME, "div")
        host = None

        # Buscamos el Shadow Root que contiene el pop-up
        for element in host_elements:
            try:
                shadow = element.shadow_root

                if shadow.find_elements(By.CSS_SELECTOR, f".{nombre_clase_popup}"):
                    host = element
                    break

            except:
                continue

        if not host:
            print("No se encontró el popup:", nombre_clase_popup)
            return False

        shadow_root = host.shadow_root

        boton_close = shadow_root.find_element(
            By.CSS_SELECTOR, "button[aria-label='Close']"
        )
        boton_close.click()

        return True

    except Exception as e:
        print("Error al cerrar el popup:", e)
        return False


# FUNCIÓN 3: Abrir la web WTA
def abrir_Web_WTA(url):

    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(10)

    aceptar_cookies(driver)

    time.sleep(5)
    cerrar_popup_weblayer(driver, "weblayer--box-web-push-subscription")

    time.sleep(1.5)
    cerrar_popup_weblayer(driver, "weblayer--box-cookieless")

    return driver


# FUNCIÓN 4: Extraer los torneos solicitados
def extraer_wta(nombres_torneos):

    # Permitimos introducir un torneo o una lista
    if isinstance(nombres_torneos, str):
        nombres_torneos = [nombres_torneos]

    url = "https://www.wtatennis.com/tournaments"
    driver = abrir_Web_WTA(url)

    tournaments = {}

    # Obtenemos los nombres de los torneos y sus enlaces
    try:
        driver.implicitly_wait(10)
        cambio_all = driver.find_element(By.CLASS_NAME, "tournament-list__status-filter")
        cambio_all.click()
    except Exception as e:
        print("No se pudo hacer clic en el filtro 'All':", e)
    driver.implicitly_wait(10)
    
    try:
        torneos = driver.find_elements(
            By.CLASS_NAME, "tournament-list__absolute-link"
        )

        for torneo in torneos:
            nombre = torneo.get_attribute("title")
            enlace = torneo.get_attribute("href")
            tournaments[nombre] = enlace

        print("Número de torneos encontrados:", len(tournaments))

        for nombre in tournaments:
            print(nombre)

    except Exception as e:
        print("Error al obtener los torneos:", e)


    torneoDatos = {}

    # Recorremos únicamente los torneos solicitados
    for nombre_torneo in nombres_torneos:

        if nombre_torneo not in tournaments:
            print("No se ha encontrado el torneo:", nombre_torneo)
            continue

        enlace = tournaments[nombre_torneo]
        driver = None

        try:
            driver = abrir_Web_WTA(enlace)

            ciudad = driver.find_element(
                By.CLASS_NAME, "tournament-header__description"
            ).text

            categoria = driver.find_element(
                By.CLASS_NAME, "tournament-header__tournament-level"
            ).get_attribute("alt")

            superficie = driver.find_element(
                By.CLASS_NAME, "tournament-header__details-surface"
            ).text

            fecha = driver.find_element(
                By.CSS_SELECTOR, "div.tournament-header__date-range"
            ).text

            botonPlayers = driver.find_element(
                By.CSS_SELECTOR, "a[data-tracking-detail='Player List']"
            )
            botonPlayers.click()

            # Extraemos las jugadoras y sus enlaces
            jugadoras = {}

            elementos = driver.find_elements(
                By.CLASS_NAME, "tournament-player-card__name"
            )

            for jugadora in elementos:
                nombre = jugadora.get_attribute("data-tracking-player-name")
                enlace_jugadora = jugadora.get_attribute("href")
                jugadoras[nombre] = enlace_jugadora

            torneoDatos[nombre_torneo] = {
                "Ciudad": ciudad,
                "Categoria": categoria,
                "Superficie": superficie,
                "Fecha": fecha,
                "Jugadoras": jugadoras
            }

        except Exception as e:
            print("Error en el torneo", nombre_torneo, ":", e)

        finally:
            if driver is not None:
                driver.quit()

    return torneoDatos



torneos = ["Mutua Madrid Open", "Dubai Duty Free Tennis Championships"]

datos = extraer_wta(torneos)

for torneo, informacion in datos.items():
    print(torneo, informacion)
