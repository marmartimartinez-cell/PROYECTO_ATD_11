import requests


def obtener_coordenadas(ciudad, pais=""):
    # Geocoding: convertir el nombre de una ciudad en coordenadas.
    url = "https://geocoding-api.open-meteo.com/v1/search"
    busqueda = ciudad + ", " + pais if pais else ciudad
    parametros = {"name": busqueda, "count": 1, "language": "en"}

    respuesta = requests.get(url, params=parametros, timeout=20)
    respuesta.raise_for_status()
    resultados = respuesta.json().get("results", [])

    if not resultados:
        raise ValueError("No se han encontrado coordenadas para " + busqueda)

    lugar = resultados[0]
    return lugar["latitude"], lugar["longitude"]


def obtener_tiempo_historico(latitud, longitud, fecha_inicio, fecha_fin):
    # Consultamos la meteorología de un intervalo ya pasado.
    url = "https://archive-api.open-meteo.com/v1/archive"
    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "start_date": fecha_inicio,
        "end_date": fecha_fin,
        "daily": [
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_mean",
            "relative_humidity_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_mean"
        ],
        "timezone": "auto"
    }

    respuesta = requests.get(url, params=parametros, timeout=30)
    respuesta.raise_for_status()
    datos = respuesta.json().get("daily", {})

    def media(variable):
        valores = []
        for valor in datos.get(variable, []):
            if valor is not None:
                valores.append(valor)
        if not valores:
            raise ValueError("Faltan datos de: " + variable)
        return round(sum(valores) / len(valores), 1)

    precipitaciones = datos.get("precipitation_sum", [])
    total_lluvia = 0
    datos_lluvia = 0
    for valor in precipitaciones:
        if valor is not None:
            total_lluvia += valor
            datos_lluvia += 1
    if datos_lluvia == 0:
        raise ValueError("Faltan datos de precipitaciones")

    # Contamos los días con lluvia apreciable (1 mm o más).
    dias_con_lluvia = 0
    for lluvia in precipitaciones:
        if lluvia is not None and lluvia >= 1:
            dias_con_lluvia += 1

    return {
        "dias_con_lluvia": dias_con_lluvia,
        "dias_analizados": datos_lluvia,
        "temperatura_media_c": media("temperature_2m_mean"),
        "temperatura_maxima_media_c": media("temperature_2m_max"),
        "temperatura_minima_media_c": media("temperature_2m_min"),
        "sensacion_termica_media_c": media("apparent_temperature_mean"),
        "humedad_media_pct": media("relative_humidity_2m_mean"),
        "precipitacion_total_mm": round(total_lluvia, 1),
        "viento_medio_kmh": media("wind_speed_10m_mean")
    }
