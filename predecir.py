from tennis_abstract import extraer_tennis_abstract

def predecir_partido(nombre1, nombre2, superficie):

    jugadoras = extraer_tennis_abstract()

    elo1 = None
    elo2 = None

    # Buscamos las puntuaciones Elo de ambas jugadoras
    for jugadora in jugadoras:

        if jugadora["nombre"].lower() == nombre1.lower():
            if jugadora[superficie].strip() != "":
                elo1 = float(jugadora[superficie])

        if jugadora["nombre"].lower() == nombre2.lower():
            if jugadora[superficie].strip() != "":
                elo2 = float(jugadora[superficie])

    if elo1 is None or elo2 is None:
        return "No se han encontrado datos de alguna de las jugadoras."

    # Calculamos las probabilidades de victoria
    diferencia = elo1 - elo2

    prob1 = 1 - (1 / (1 + 10 ** (diferencia / 400)))
    prob2 = 1 - prob1

    return {
        "jugadora1": nombre1,
        "elo1": elo1,
        "probabilidad1": round(prob1 * 100, 2),
        "jugadora2": nombre2,
        "elo2": elo2,
        "probabilidad2": round(prob2 * 100, 2)}




######### EL CÓDIGO DE ABAJO DEBE IR EN EL SERVIDOR
resultado = predecir_partido("Aryna Sabalenka", "Coco Gauff", "arcilla")

print(resultado["jugadora1"], ":", resultado["probabilidad1"], "%")
print(resultado["jugadora2"], ":", resultado["probabilidad2"], "%")