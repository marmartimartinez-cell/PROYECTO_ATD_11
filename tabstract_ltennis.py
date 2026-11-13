def comparar_rankings(cantidad):
    from tennis_abstract import extraer_tennis_abstract
    from livetennis import extraer_live_tennis


    # Extraemos los rankings actualizados
    ranking_elo = extraer_tennis_abstract()
    ranking_wta = extraer_live_tennis()

    diferencias = []

    # Buscamos las jugadoras que aparecen en ambos rankings
    for jugadora_elo in ranking_elo:
        for jugadora_wta in ranking_wta:

            nombre1 = jugadora_elo["nombre"].lower().strip()
            nombre2 = jugadora_wta["nombre"].lower().strip()

            if nombre1 == nombre2:

                puesto_elo = int(jugadora_elo["ranking"])
                puesto_wta = int(jugadora_wta["ranking"])

                diferencia = puesto_wta - puesto_elo

                diferencias.append({
                    "nombre": jugadora_elo["nombre"],
                    "ranking_wta": puesto_wta,
                    "ranking_elo": puesto_elo,
                    "diferencia": diferencia
                })

                break

    # Ordenamos por diferencia de posiciones
    def obtener_diferencia(jugadora):
        return jugadora["diferencia"]

    diferencias.sort(key=obtener_diferencia, reverse=True)

    infravaloradas = []
    sobrevaloradas = []

    for jugadora in diferencias:
        if jugadora["diferencia"] > 0:
            infravaloradas.append(jugadora)

        if jugadora["diferencia"] < 0:
            sobrevaloradas.append(jugadora)

    return {
        "infravaloradas": infravaloradas[:cantidad],
        "sobrevaloradas": sobrevaloradas[-cantidad:][::-1]
    }



resultado = comparar_rankings(10)

print("JUGADORAS INFRAVALORADAS")
for jugadora in resultado["infravaloradas"]:
    print(jugadora)

print("\nJUGADORAS SOBREVALORADAS")
for jugadora in resultado["sobrevaloradas"]:
    print(jugadora)
