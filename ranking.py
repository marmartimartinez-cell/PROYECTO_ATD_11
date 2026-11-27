import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException

# ==========================================
# CONFIGURACIÓN
# ==========================================
URL = "https://www.wtatennis.com/rankings/singles"
MAX_JUGADORAS = 300

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
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
        pass

def cerrar_popup_weblayer(driver, nombre_clase_popup):
    try:
        host_elements = driver.find_elements(By.TAG_NAME, "div")
        host = None
        for element in host_elements:
            try:
                shadow = element.shadow_root
                if shadow.find_elements(By.CSS_SELECTOR, f".{nombre_clase_popup}"):
                    host = element
                    break
            except:
                continue
        
        if not host:
            return False

        shadow_root = host.shadow_root
        boton_close = shadow_root.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
        boton_close.click()
        return True
    except Exception:
        return False

def cargar_jugadoras(driver, limite):
    print(f"Verificando si es necesario cargar hasta {limite} jugadoras...")
    driver.implicitly_wait(5)
    ultimo_total = -1
    sin_avance = 0

    while True:
        filas = driver.find_elements(By.CSS_SELECTOR, "tr.player-row")
        if len(filas) <= ultimo_total:
            sin_avance += 1
        else:
            sin_avance = 0
        ultimo_total = len(filas)
        if sin_avance >= 2:
            print("No aparecen más jugadoras; detenemos la carga.")
            break
        
        if len(filas) >= limite:
            print(f"✅ Se han cargado {len(filas)} jugadoras. Límite alcanzado.")
            break
            
        try:
            boton = driver.find_element(By.CSS_SELECTOR, "button.js-load-more")
            
            if not boton.is_displayed():
                print(f"⚠️ El botón 'Load More' ya no está visible. Total cargado: {len(filas)}")
                break
                
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", boton)
            time.sleep(2) 
            
        except NoSuchElementException:
            print(f"✅ No se encontró el botón 'Load More'. Total cargado: {len(filas)}")
            break
        except Exception as e:
            print(f"❌ Error al intentar cargar más jugadoras: {e}")
            break

def extraer_datos_ranking(driver):
    print("Extrayendo datos (usando el motor interno de Selenium)...")
    script = """
    let datos = {};
    document.querySelectorAll('tr.player-row').forEach(fila => {
        let nombreElem = fila.querySelector('span.player-cell__name');
        let puntosElem = fila.querySelector('td.player-row__cell--points');
        let rankElem = fila.querySelector('td.player-row__cell--rank span.player-row__rank');
        
        if (nombreElem && puntosElem && rankElem) {
            let nombre = nombreElem.innerText.trim();
            let puntos = parseInt(puntosElem.innerText.trim().replace(/,/g, ''));
            let rank = parseInt(rankElem.innerText.trim());
            datos[nombre] = {rank: rank, puntos: puntos};
        }
    });
    return datos;
    """
    datos = driver.execute_script(script)
    print(f"✅ Datos extraídos: {len(datos)} jugadoras.")
    return datos

# ==========================================
# SCRIPT PRINCIPAL
# ==========================================

def cambios_ranking(cantidad=10, limite=300):
    """Compara el ranking WTA actual con el de la semana anterior."""
    driver = abrir_Web_WTA(URL)
    try:
        print("Extrayendo ranking de la semana actual...")
        cargar_jugadoras(driver, limite)
        time.sleep(1)
        datos_actuales = extraer_datos_ranking(driver)

        print("Seleccionando la semana anterior...")
        driver.implicitly_wait(10)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)

        boton_filtro = driver.find_element(By.CSS_SELECTOR, "button.js-filter-btn")
        driver.execute_script("arguments[0].click();", boton_filtro)
        time.sleep(1.5)

        boton_fecha = driver.find_element(By.CSS_SELECTOR, "button[data-target-screen='date']")
        driver.execute_script("arguments[0].click();", boton_fecha)
        time.sleep(1.5)

        espera = WebDriverWait(driver, 10)
        fila_actual = espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.date-picker__row--selected")))
        lunes_actual = datetime.strptime(fila_actual.get_attribute("data-monday"), "%Y-%m-%d")
        lunes_anterior = lunes_actual - timedelta(days=7)
        selector = "tr.date-picker__row[data-monday='" + lunes_anterior.strftime("%Y-%m-%d") + "']"
        fila_anterior = driver.find_element(By.CSS_SELECTOR, selector)
        dia = str(lunes_anterior.day)
        casilla = fila_anterior.find_element(By.XPATH, ".//span[@class='date-picker__cell-data' and normalize-space(text())='" + dia + "']")
        driver.execute_script("arguments[0].click();", casilla)

        boton_ver = driver.find_element(By.CSS_SELECTOR, "button.js-filter-close")
        driver.execute_script("arguments[0].click();", boton_ver)
        time.sleep(4)

        cargar_jugadoras(driver, limite)
        time.sleep(1)
        datos_anteriores = extraer_datos_ranking(driver)
    finally:
        driver.quit()

    ganadores_puntos = []
    perdedores_puntos = []
    subidas_puestos = []
    bajadas_puestos = []

    for nombre, actual in datos_actuales.items():
        if nombre not in datos_anteriores:
            continue
        anterior = datos_anteriores[nombre]
        puntos = actual["puntos"] - anterior["puntos"]
        puestos = anterior["rank"] - actual["rank"]

        if puntos > 0:
            ganadores_puntos.append({"nombre": nombre, "diferencia": puntos})
        elif puntos < 0:
            perdedores_puntos.append({"nombre": nombre, "diferencia": puntos})
        if puestos > 0:
            subidas_puestos.append({"nombre": nombre, "diferencia": puestos})
        elif puestos < 0:
            bajadas_puestos.append({"nombre": nombre, "diferencia": puestos})

    def diferencia(jugadora):
        return jugadora["diferencia"]

    ganadores_puntos.sort(key=diferencia, reverse=True)
    perdedores_puntos.sort(key=diferencia)
    subidas_puestos.sort(key=diferencia, reverse=True)
    bajadas_puestos.sort(key=diferencia)

    return {
        "ganadores_puntos": ganadores_puntos[:cantidad],
        "perdedores_puntos": perdedores_puntos[:cantidad],
        "subidas_puestos": subidas_puestos[:cantidad],
        "bajadas_puestos": bajadas_puestos[:cantidad]
    }
