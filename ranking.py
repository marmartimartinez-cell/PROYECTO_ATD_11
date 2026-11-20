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
    
    while True:
        filas = driver.find_elements(By.CSS_SELECTOR, "tr.player-row")
        
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
if __name__ == "__main__":
    driver = abrir_Web_WTA(URL)

    # 1. EXTRAER SEMANA ACTUAL
    print("\n--- SEMANA ACTUAL ---")
    cargar_jugadoras(driver, MAX_JUGADORAS)
    time.sleep(1) 
    datos_actuales = extraer_datos_ranking(driver)
    
    # 2. CAMBIAR A LA SEMANA ANTERIOR
    print("\n--- CAMBIANDO A LA SEMANA ANTERIOR ---")
    driver.implicitly_wait(10)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1.5)
    
    btn_filter = driver.find_element(By.CSS_SELECTOR, "button.js-filter-btn")
    driver.execute_script("arguments[0].click();", btn_filter)
    time.sleep(1.5)
    
    btn_date = driver.find_element(By.CSS_SELECTOR, "button[data-target-screen='date']")
    driver.execute_script("arguments[0].click();", btn_date)
    time.sleep(1.5)

    wait = WebDriverWait(driver, 10)
    fila_seleccionada = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.date-picker__row--selected")))
    fecha_lunes_str = fila_seleccionada.get_attribute("data-monday")
    
    fecha_lunes = datetime.strptime(fecha_lunes_str, "%Y-%m-%d")
    fecha_lunes_anterior = fecha_lunes - timedelta(days=7)
    fecha_lunes_anterior_str = fecha_lunes_anterior.strftime("%Y-%m-%d")
    dia_a_clickear = str(fecha_lunes_anterior.day)

    selector_fila_anterior = f"tr.date-picker__row[data-monday='{fecha_lunes_anterior_str}']"
    fila_anterior = driver.find_element(By.CSS_SELECTOR, selector_fila_anterior)
    elemento_dia = fila_anterior.find_element(By.XPATH, f".//span[@class='date-picker__cell-data' and normalize-space(text())='{dia_a_clickear}']")
    driver.execute_script("arguments[0].click();", elemento_dia)

    boton_ver = driver.find_element(By.CSS_SELECTOR, "button.js-filter-close")
    driver.execute_script("arguments[0].click();", boton_ver)
    
    print("Esperando a que la página recargue los datos de la semana anterior...")
    time.sleep(4) 
    
    # 3. EXTRAER SEMANA ANTERIOR
    cargar_jugadoras(driver, MAX_JUGADORAS)
    time.sleep(1)
    datos_anteriores = extraer_datos_ranking(driver)
    
    driver.quit()

    # 4. COMPARACIONES
    cambios_puntos = []
    cambios_rank = []

    for nombre, actual in datos_actuales.items():
        if nombre in datos_anteriores:
            anterior = datos_anteriores[nombre]
            
            diff_puntos = actual["puntos"] - anterior["puntos"]
            if diff_puntos != 0:
                cambios_puntos.append({"nombre": nombre, "diff": diff_puntos, "actual": actual["puntos"], "anterior": anterior["puntos"]})
            
            diff_rank = anterior["rank"] - actual["rank"]
            if diff_rank != 0:
                cambios_rank.append({"nombre": nombre, "diff": diff_rank, "actual": actual["rank"], "anterior": anterior["rank"]})

    ganadores_pts = [p for p in cambios_puntos if p["diff"] > 0]
    perdedores_pts = [p for p in cambios_puntos if p["diff"] < 0]
    subieron_rank = [r for r in cambios_rank if r["diff"] > 0]
    bajaron_rank = [r for r in cambios_rank if r["diff"] < 0]

    top_ganadores_puntos = sorted(ganadores_pts, key=lambda x: x["diff"], reverse=True)[:10]
    top_perdedores_puntos = sorted(perdedores_pts, key=lambda x: x["diff"])[:10]
    top_subieron_rank = sorted(subieron_rank, key=lambda x: x["diff"], reverse=True)[:10]
    top_bajaron_rank = sorted(bajaron_rank, key=lambda x: x["diff"])[:10]

    # ==========================================
    # 5. MOSTRAR RESULTADOS (FORMATO LISTA)
    # ==========================================
    print("\n" + "="*50)
    print("🏆 TOP 10 - JUGADORAS QUE MÁS PUNTOS HAN GANADO")
    print("="*50)
    if not top_ganadores_puntos:
        print("No hubo jugadoras que ganaran puntos.")
    else:
        for i, p in enumerate(top_ganadores_puntos, 1):
            print(f"{i}. {p['nombre']} (+{p['diff']} pts)")

    print("\n" + "="*50)
    print("📉 TOP 10 - JUGADORAS QUE MÁS PUNTOS HAN PERDIDO")
    print("="*50)
    if not top_perdedores_puntos:
        print("No hubo jugadoras que perdieran puntos.")
    else:
        for i, p in enumerate(top_perdedores_puntos, 1):
            print(f"{i}. {p['nombre']} ({p['diff']} pts)")

    print("\n" + "="*50)
    print("🚀 TOP 10 - JUGADORAS QUE MÁS PUESTOS HAN SUBIDO")
    print("="*50)
    if not top_subieron_rank:
        print("Nadie subió puestos esta semana.")
    else:
        for i, r in enumerate(top_subieron_rank, 1):
            print(f"{i}. {r['nombre']} (+{r['diff']} puestos)")

    print("\n" + "="*50)
    print("⚠️ TOP 10 - JUGADORAS QUE MÁS PUESTOS HAN BAJADO")
    print("="*50)
    if not top_bajaron_rank:
        print("Nadie bajó puestos esta semana.")
    else:
        for i, r in enumerate(top_bajaron_rank, 1):
            print(f"{i}. {r['nombre']} ({r['diff']} puestos)")