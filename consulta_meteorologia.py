import re
from datetime import date, timedelta

from wta import extraer_wta
from weatherAPI import obtener_coordenadas, obtener_tiempo_historico


MESES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


def convertir_fechas(texto):
    # Ejemplos: 'Apr 21 - May 3, 2026' y 'Jun 9 - 15, 2026'.
    patron = r"([A-Za-z]+)\s+(\d{1,2})(?:,?\s+(\d{4}))?\s*[-–—]\s*(?:([A-Za-z]+)\s+)?(\d{1,2})(?:,?\s+(\d{4}))?"
    resultado = re.search(patron, texto.replace("\n", " "))

    if resultado is None:
        raise ValueError("Formato de fecha de la WTA no reconocido: " + texto)

    mes_inicio, dia_inicio, anio_inicio, mes_fin, dia_fin, anio_fin = resultado.groups()
    primer_mes = MESES[mes_inicio[:3].lower()]
    ultimo_mes = MESES[mes_fin[:3].lower()] if mes_fin else primer_mes

    if not anio_inicio and not anio_fin:
        raise ValueError("La WTA no indica el año en: " + texto)

    anio_final = int(anio_fin or anio_inicio)
    anio_inicial = int(anio_inicio or anio_fin)
    if not anio_inicio and primer_mes > ultimo_mes:
        anio_inicial -= 1

    inicio = date(anio_inicial, primer_mes, int(dia_inicio))
    fin = date(anio_final, ultimo_mes, int(dia_fin))
    if fin < inicio:
        raise ValueError("Fechas del torneo no válidas: " + texto)

    return inicio, fin


def mismo_periodo_ano_anterior(fecha, anos_atras):
    # El 29 de febrero se sustituye por el 28 en años no bisiestos.
    try:
        return fecha.replace(year=fecha.year - anos_atras)
    except ValueError:
        return fecha.replace(year=fecha.year - anos_atras, day=28)


def interpretar_tiempo(promedio):
    # Interpretamos la frecuencia histórica de días con lluvia.
    porcentaje_lluvia = 100 * promedio["dias_con_lluvia"] / promedio["dias_analizados"]

    if porcentaje_lluvia < 15:
        lluvia = "La lluvia fue poco frecuente en estas fechas."
    elif porcentaje_lluvia < 40:
        lluvia = "Se registraron algunos días de lluvia en estas fechas."
    else:
        lluvia = "La lluvia fue relativamente frecuente en estas fechas."

    # Interpretamos la velocidad media del viento.
    viento_medio = promedio["viento_medio_kmh"]
    if viento_medio < 10:
        viento = "En general, hubo poco viento."
    elif viento_medio < 20:
        viento = "Normalmente, el viento fue suave."
    elif viento_medio < 30:
        viento = "El viento fue moderado."
    else:
        viento = "Se registraron vientos considerables."

    # Interpretamos la temperatura media.
    temperatura = promedio["temperatura_media_c"]
    if temperatura < 12:
        temperatura_texto = "Las temperaturas fueron frescas."
    elif temperatura < 25:
        temperatura_texto = "Las temperaturas fueron suaves."
    elif temperatura < 30:
        temperatura_texto = "Las temperaturas fueron cálidas."
    else:
        temperatura_texto = "Las temperaturas fueron altas."

    return {
        "lluvia": lluvia,
        "viento": viento,
        "temperatura": temperatura_texto,
        "porcentaje_dias_con_lluvia": round(porcentaje_lluvia, 1)
    }


def meteorologia_torneo(nombres_torneos, cantidad_anios=3):
    if cantidad_anios < 1:
        raise ValueError("La cantidad de años debe ser mayor que cero")

    # El scraper WTA se ejecuta una única vez para todos los torneos pedidos.
    torneos = extraer_wta(nombres_torneos)
    resultados = {}

    for nombre, informacion in torneos.items():
        try:
            ubicacion = informacion["Ciudad"].replace("•", ",")
            partes = ubicacion.split(",", 1)
            ciudad = partes[0].strip()
            pais = partes[1].strip() if len(partes) > 1 else ""

            inicio, fin = convertir_fechas(informacion["Fecha"])
            latitud, longitud = obtener_coordenadas(ciudad, pais)

            historial = []
            anos_atras = 1

            # Elegimos los tres intervalos históricos completos más recientes.
            while len(historial) < cantidad_anios and anos_atras <= cantidad_anios + 8:
                inicio_h = mismo_periodo_ano_anterior(inicio, anos_atras)
                fin_h = mismo_periodo_ano_anterior(fin, anos_atras)
                anos_atras += 1

                if fin_h >= date.today() - timedelta(days=7):
                    continue

                datos = obtener_tiempo_historico(
                    latitud, longitud, inicio_h.isoformat(), fin_h.isoformat()
                )
                datos["anio"] = inicio_h.year
                datos["periodo"] = inicio_h.isoformat() + " / " + fin_h.isoformat()
                historial.append(datos)

            if not historial:
                raise ValueError("No hay intervalos históricos disponibles")

            # Promedio de las condiciones de los años consultados.
            promedio = {}
            for campo in historial[0]:
                if campo not in ("anio", "periodo"):
                    total = 0
                    for anio in historial:
                        total += anio[campo]
                    promedio[campo] = round(total / len(historial), 1)

            resultados[nombre] = {
                "ciudad": ciudad,
                "pais": pais,
                "fecha_wta": informacion["Fecha"],
                "superficie": informacion["Superficie"],
                "latitud": latitud,
                "longitud": longitud,
                "historico": historial,
                "promedio": promedio,
                "interpretacion": interpretar_tiempo(promedio)
            }

        except Exception as error:
            resultados[nombre] = {"error": str(error)}

    return resultados


if __name__ == "__main__":
    entrada = input("Nombre del torneo (o varios separados por comas): ")
    nombres = []
    for nombre in entrada.split(","):
        if nombre.strip():
            nombres.append(nombre.strip())

    try:
        resultados = meteorologia_torneo(nombres)
        for torneo, datos in resultados.items():
            print("\nTORNEO:", torneo)
            if "error" in datos:
                print("Error:", datos["error"])
                continue
            print("Ciudad:", datos["ciudad"], "-", datos["pais"])
            print("Fechas WTA:", datos["fecha_wta"])
            print("Histórico:")
            for anio in datos["historico"]:
                print(anio)
            print("Promedio histórico:", datos["promedio"])
            print("Interpretación de las condiciones habituales:")
            print("  Lluvia:", datos["interpretacion"]["lluvia"])
            print("  Viento:", datos["interpretacion"]["viento"])
            print("  Temperatura:", datos["interpretacion"]["temperatura"])
            print("  Porcentaje de días con lluvia:", datos["interpretacion"]["porcentaje_dias_con_lluvia"], "%")
        if not resultados:
            print("No se ha encontrado ningún torneo. Revisa el nombre que aparece en la WTA.")
    except Exception as error:
        print("No se pudo completar la consulta:", error)
