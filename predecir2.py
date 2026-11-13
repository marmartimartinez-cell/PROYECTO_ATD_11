from tennis_abstract import extraer_tennis_abstract

def comparar_jugadoras(nombre1, nombre2):

    jugadoras = extraer_tennis_abstract()

    # Buscamos las dos jugadoras
    jugadora1 = None
    jugadora2 = None

    for jugadora in jugadoras:
        if jugadora["nombre"].lower() == nombre1.lower():
            jugadora1 = jugadora

        if jugadora["nombre"].lower() == nombre2.lower():
            jugadora2 = jugadora

    if jugadora1 is None or jugadora2 is None:
        return "No se han encontrado ambas jugadoras."

    resultados = {}

    # Calculamos la probabilidad para cada tipo de Elo
    superficies = ["elo", "dura", "arcilla", "hierba"]

    for superficie in superficies:

        if jugadora1[superficie].strip() != "" and jugadora2[superficie].strip() != "":

            elo1 = float(jugadora1[superficie])
            elo2 = float(jugadora2[superficie])

            diferencia = elo1 - elo2

            prob1 = 1 - (1 / (1 + 10 ** (diferencia / 400)))
            prob2 = 1 - prob1

            resultados[superficie] = {
                "probabilidad1": round(prob1 * 100, 2),
                "probabilidad2": round(prob2 * 100, 2)
            }

        else:
            resultados[superficie] = None

    return resultados

resultado = comparar_jugadoras("Aryna Sabalenka", "Coco Gauff")

for superficie in resultado:

    if resultado[superficie] is not None:
        print("\n", superficie.upper())
        print("Aryna Sabalenka:", resultado[superficie]["probabilidad1"], "%")
        print("Coco Gauff:", resultado[superficie]["probabilidad2"], "%")