from tennis_abstract import extraer_tennis_abstract
from livetennis import extraer_live_tennis, normalizar_nombre


def comparar_rankings(cantidad=10, top=100):
    """Compara el ranking WTA (Live Tennis) con el ranking Elo (Tennis Abstract).
    diferencia = puesto WTA - puesto Elo
      > 0 -> infravalorada (está mejor en Elo que en la WTA)
      < 0 -> sobrevalorada (está peor en Elo que en la WTA)
    Solo se comparan las 'top' primeras de la WTA."""

    # 1. Extraemos los dos rankings
    ranking_elo = extraer_tennis_abstract()
    ranking_wta = extraer_live_tennis()[:top]

    # 2. Diccionario: nombre normalizado -> puesto en el Elo
    #    (Tennis Abstract no normaliza, así que lo hacemos aquí)
    puestos_elo = {}
    for jugadora in ranking_elo:
        nombre = normalizar_nombre(jugadora["nombre"])
        puestos_elo[nombre] = int(jugadora["ranking"])

    # 3. Buscamos cada jugadora de la WTA en el Elo y calculamos la diferencia
    diferencias = []
    sin_cruzar = []

    for jugadora in ranking_wta:
        nombre = jugadora["nombre_normalizado"]

        if nombre in puestos_elo:
            puesto_wta = int(jugadora["ranking"])
            puesto_elo = puestos_elo[nombre]

            diferencias.append({
                "nombre": jugadora["nombre"],
                "ranking_wta": puesto_wta,
                "ranking_elo": puesto_elo,
                "diferencia": puesto_wta - puesto_elo
            })
        else:
            sin_cruzar.append(jugadora["nombre"])

    # 4. Ordenamos de mayor a menor diferencia
    def obtener_diferencia(jugadora):
        return jugadora["diferencia"]

    diferencias.sort(key=obtener_diferencia, reverse=True)

    # 5. Separamos infravaloradas y sobrevaloradas
    infravaloradas = []
    sobrevaloradas = []

    for jugadora in diferencias:
        if jugadora["diferencia"] > 0:
            infravaloradas.append(jugadora)
        if jugadora["diferencia"] < 0:
            sobrevaloradas.append(jugadora)

    # Las sobrevaloradas están ordenadas de -1 a la más negativa:
    # cogemos las últimas y les damos la vuelta para que la peor salga primero
    return {
        "infravaloradas": infravaloradas[:cantidad],
        "sobrevaloradas": sobrevaloradas[-cantidad:][::-1],
        "sin_cruzar": sin_cruzar
    }


# Esto solo se ejecuta si lanzas este fichero directamente (py tabstract_ltennis.py)
if __name__ == '__main__':
    resultado = comparar_rankings(10)

    print("\nJUGADORAS INFRAVALORADAS (mejor en Elo que en la WTA)")
    for j in resultado["infravaloradas"]:
        print(j["nombre"], "| WTA:", j["ranking_wta"], "| Elo:", j["ranking_elo"], "| Diferencia:", j["diferencia"])

    print("\nJUGADORAS SOBREVALORADAS (peor en Elo que en la WTA)")
    for j in resultado["sobrevaloradas"]:
        print(j["nombre"], "| WTA:", j["ranking_wta"], "| Elo:", j["ranking_elo"], "| Diferencia:", j["diferencia"])

    print("\nJugadoras del top que no se han podido cruzar:", len(resultado["sin_cruzar"]))
    print(resultado["sin_cruzar"])
