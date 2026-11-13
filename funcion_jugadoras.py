from tennis_abstract import extraer_tennis_abstract

def mejores_superficie(superficie, cantidad):

    jugadoras = extraer_tennis_abstract()
    ranking = []

    # Guardamos únicamente el nombre y el Elo de la superficie elegida
    for jugadora in jugadoras:
        if jugadora[superficie].strip() != "":
            ranking.append({
                "nombre": jugadora["nombre"],
                "elo": float(jugadora[superficie])
            })

    # Ordenamos de mayor a menor Elo
    def obtener_elo(jugadora):
        return jugadora["elo"]

    ranking.sort(key=obtener_elo, reverse=True)

    return ranking[:cantidad]


######### EL CÓDIGO DE ABAJO DEBE IR EN EL SERVIDOR
superficie = "arcilla"
respuesta = mejores_superficie(superficie, 50)
print(f"Ranking de jugadoras en función de la superficie: {superficie}")
for i, jugadora in enumerate(respuesta):
    print(i+1, jugadora["nombre"], ":", jugadora["elo"])