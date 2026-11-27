from selenium import webdriver
from selenium.webdriver.common.by import By


def extraer_tennis_abstract():
    driver = webdriver.Chrome()
    try:
        driver.get("https://tennisabstract.com")
        enlace = driver.find_element(By.LINK_TEXT, "... All Women's Elo Ratings")
        driver.get(enlace.get_attribute("href"))

        filas = driver.find_elements(By.CSS_SELECTOR, "#reportable tbody tr")
        jugadoras = []
        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if len(columnas) > 10:
                jugadoras.append({
                    "ranking": columnas[0].text,
                    "nombre": columnas[1].text,
                    "elo": columnas[3].text,
                    "dura": columnas[6].text,
                    "arcilla": columnas[8].text,
                    "hierba": columnas[10].text
                })
        return jugadoras
    finally:
        driver.quit()
