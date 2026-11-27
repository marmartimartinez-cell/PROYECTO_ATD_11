from selenium import webdriver
from selenium.webdriver.common.by import By
import time


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


def aceptar_cookies(driver):
    try:
        aceptar = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        aceptar.click()
    except Exception:
        pass  # Puede que el aviso de cookies ya no aparezca.


def cerrar_popup_weblayer(driver, nombre_clase_popup):
    try:
        host_elements = driver.find_elements(By.TAG_NAME, "div")
        for element in host_elements:
            try:
                shadow = element.shadow_root
                if shadow.find_elements(By.CSS_SELECTOR, f".{nombre_clase_popup}"):
                    boton = shadow.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
                    boton.click()
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def obtener_catalogo_torneos():
    driver = abrir_Web_WTA("https://www.wtatennis.com/tournaments")
    tournaments = {}
    try:
        try:
            filtro = driver.find_element(By.CLASS_NAME, "tournament-list__status-filter")
            try:
                filtro.click()
            except Exception:
                driver.execute_script("arguments[0].click();", filtro)
        except Exception:
            pass

        time.sleep(3)
        torneos = driver.find_elements(By.CLASS_NAME, "tournament-list__absolute-link")
        for torneo in torneos:
            nombre = torneo.get_attribute("title") or torneo.text.strip()
            enlace = torneo.get_attribute("href")
            if nombre and enlace:
                tournaments[nombre] = enlace
    finally:
        driver.quit()

    if not tournaments:
        raise ValueError("La WTA no ha devuelto torneos. Revisad la web y los selectores de Selenium.")
    return tournaments


def listar_torneos():
    # Devuelve los nombres tal como aparecen ahora en la WTA.
    return sorted(obtener_catalogo_torneos(), key=str.casefold)


def extraer_wta(nombres_torneos):
    if isinstance(nombres_torneos, str):
        nombres_torneos = [nombres_torneos]

    tournaments = obtener_catalogo_torneos()
    torneoDatos = {}

    for nombre_torneo in nombres_torneos:
        nombre_encontrado = None
        for nombre in tournaments:
            if nombre.strip().casefold() == nombre_torneo.strip().casefold():
                nombre_encontrado = nombre
                break

        if nombre_encontrado is None:
            coincidencias = []
            for nombre in tournaments:
                if nombre_torneo.strip().casefold() in nombre.casefold():
                    coincidencias.append(nombre)
            if len(coincidencias) == 1:
                nombre_encontrado = coincidencias[0]
            elif len(coincidencias) > 1:
                raise ValueError("Nombre de torneo ambiguo: " + nombre_torneo + ". Coincidencias: " + ", ".join(coincidencias))

        if nombre_encontrado is None:
            raise ValueError("No se ha encontrado el torneo: " + nombre_torneo)

        driver = abrir_Web_WTA(tournaments[nombre_encontrado])
        try:
            ciudad = driver.find_element(By.CLASS_NAME, "tournament-header__description").text
            categoria = driver.find_element(By.CLASS_NAME, "tournament-header__tournament-level").get_attribute("alt")
            superficie = driver.find_element(By.CLASS_NAME, "tournament-header__details-surface").text
            fecha = driver.find_element(By.CSS_SELECTOR, "div.tournament-header__date-range").text
            torneoDatos[nombre_encontrado] = {
                "Ciudad": ciudad,
                "Categoria": categoria,
                "Superficie": superficie,
                "Fecha": fecha
            }
        finally:
            driver.quit()

    return torneoDatos
