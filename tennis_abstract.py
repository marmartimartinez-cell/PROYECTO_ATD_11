def extraer_tennis_abstract():

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    
    driver = webdriver.Chrome()
    driver.get("https://tennisabstract.com")

    rank_elo = driver.find_element(By.LINK_TEXT, "... All Women's Elo Ratings")
    enlace = rank_elo.get_attribute("href")
    driver.get(enlace)

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

    driver.quit()
    return jugadoras