"""Cliente TCP del proyecto ATD. Ejecutar: python cliente.py"""

import argparse
import json
import socket

MAX_MENSAJE = 1_000_000


def enviar_mensaje(conexion, datos):
    mensaje = json.dumps(datos, ensure_ascii=False) + "\n"
    conexion.sendall(mensaje.encode("utf-8"))


def recibir_mensaje(conexion):
    # El salto de línea marca el final del mensaje (TCP no conserva mensajes).
    with conexion.makefile("rb") as archivo:
        linea = archivo.readline(MAX_MENSAJE + 1)
    if not linea:
        raise ConnectionError("La conexión se ha cerrado sin recibir una respuesta")
    if len(linea) > MAX_MENSAJE or not linea.endswith(b"\n"):
        raise ValueError("Mensaje demasiado largo o incompleto")
    return json.loads(linea.decode("utf-8"))


def solicitar_torneos(consultar):
    lista = []
    respuesta = input("¿Quieres ver la lista de torneos de la WTA? (s/n): ").strip().lower()
    if respuesta == "s":
        consulta = {"operacion": "listar_torneos", "parametros": {}}
        recibido = consultar(consulta)
        if recibido.get("ok"):
            lista = recibido["resultado"]
            print("\nTORNEOS DISPONIBLES")
            for i, nombre in enumerate(lista, 1):
                print(str(i) + ". " + nombre)
        else:
            print("No se pudo cargar la lista:", recibido.get("error"))

    if lista:
        texto = input("Escribe los números separados por comas: ").strip()
        nombres = []
        for parte in texto.split(","):
            numero = int(parte.strip())
            if numero < 1 or numero > len(lista):
                raise ValueError("Número de torneo fuera de la lista: " + str(numero))
            nombres.append(lista[numero - 1])
        return nombres

    texto = input("Nombres de los torneos separados por comas: ").strip()
    nombres = []
    for nombre in texto.split(","):
        if nombre.strip():
            nombres.append(nombre.strip())
    return nombres


def pedir_peticion(opcion, consultar):
    if opcion == "1":
        nombre1 = input("Primera jugadora: ").strip()
        nombre2 = input("Segunda jugadora: ").strip()
        modo = input("¿Una superficie (1) o todas (2)?: ").strip()
        parametros = {"jugadora1": nombre1, "jugadora2": nombre2}
        if modo == "1":
            parametros["superficie"] = input("Superficie (dura/arcilla/hierba): ").strip()
            return {"operacion": "predecir_partido", "parametros": parametros}
        if modo == "2":
            return {"operacion": "comparar_jugadoras", "parametros": parametros}
        raise ValueError("Debes elegir 1 o 2")

    if opcion == "2":
        cantidad = input("¿Cuántas jugadoras mostrar? (por defecto 10): ").strip() or "10"
        top = input("¿Entre cuántas primeras del ranking WTA? (por defecto 100): ").strip() or "100"
        return {"operacion": "comparar_rankings", "parametros": {"cantidad": cantidad, "top": top}}

    if opcion == "3":
        cantidad = input("¿Cuántas jugadoras mostrar por lista? (por defecto 10): ").strip() or "10"
        return {"operacion": "cambios_ranking", "parametros": {"cantidad": cantidad}}

    if opcion == "4":
        superficie = input("Superficie (dura/arcilla/hierba): ").strip()
        cantidad = input("¿Cuántas jugadoras mostrar? (por defecto 10): ").strip() or "10"
        return {"operacion": "mejores_superficie", "parametros": {"superficie": superficie, "cantidad": cantidad}}

    if opcion == "5":
        nombres = solicitar_torneos(consultar)
        anios = input("¿Cuántos años anteriores analizar? (por defecto 3): ").strip() or "3"
        return {"operacion": "meteorologia_torneo", "parametros": {"torneos": nombres, "anios": anios}}

    if opcion == "6":
        return {"operacion": "estado", "parametros": {}}

    raise ValueError("Opción no válida")


def mostrar_resultado(peticion, respuesta):
    if not respuesta.get("ok"):
        print("\nERROR:", respuesta.get("error", "Error desconocido"))
        return

    resultado = respuesta.get("resultado")
    operacion = peticion["operacion"]
    print("\n" + "=" * 55)

    if operacion == "estado":
        print(resultado["mensaje"])

    elif operacion == "predecir_partido":
        print(resultado["jugadora1"], ":", resultado["probabilidad1"], "% (Elo:", resultado["elo1"], ")")
        print(resultado["jugadora2"], ":", resultado["probabilidad2"], "% (Elo:", resultado["elo2"], ")")

    elif operacion == "comparar_jugadoras":
        print(resultado["jugadora1"], "frente a", resultado["jugadora2"])
        for superficie, datos in resultado["superficies"].items():
            if datos is None:
                print(superficie.upper() + ": sin datos suficientes")
            else:
                print(superficie.upper() + ":", datos["probabilidad1"], "% /", datos["probabilidad2"], "%")

    elif operacion == "comparar_rankings":
        for clave, titulo in (("infravaloradas", "INFRAVALORADAS"), ("sobrevaloradas", "SOBREVALORADAS")):
            print("\n" + titulo)
            for i, jugadora in enumerate(resultado[clave], 1):
                print(i, jugadora["nombre"], "| WTA:", jugadora["ranking_wta"], "| Elo:", jugadora["ranking_elo"], "| Diferencia:", jugadora["diferencia"])
        print("\nSin poder cruzar:", len(resultado["sin_cruzar"]))

    elif operacion == "cambios_ranking":
        titulos = (("ganadores_puntos", "MÁS PUNTOS GANADOS"), ("perdedores_puntos", "MÁS PUNTOS PERDIDOS"), ("subidas_puestos", "MÁS PUESTOS SUBIDOS"), ("bajadas_puestos", "MÁS PUESTOS BAJADOS"))
        for clave, titulo in titulos:
            print("\n" + titulo)
            for i, jugadora in enumerate(resultado[clave], 1):
                print(i, jugadora["nombre"], "| Cambio:", jugadora["diferencia"])

    elif operacion == "mejores_superficie":
        for i, jugadora in enumerate(resultado, 1):
            print(i, jugadora["nombre"], "| Elo:", jugadora["elo"])

    elif operacion == "meteorologia_torneo":
        for nombre, datos in resultado.items():
            print("\nTORNEO:", nombre)
            if "error" in datos:
                print("Error:", datos["error"])
                continue
            print("Ciudad:", datos["ciudad"], "-", datos["pais"])
            print("Fechas:", datos["fecha_wta"])
            for anio in datos["historico"]:
                print("Año", anio["anio"], "| T. media:", anio["temperatura_media_c"], "°C | Lluvia:", anio["precipitacion_total_mm"], "mm")
            promedio = datos["promedio"]
            print("Promedio: temperatura", promedio["temperatura_media_c"], "°C; lluvia", promedio["precipitacion_total_mm"], "mm; viento", promedio["viento_medio_kmh"], "km/h")
            interpretacion = datos["interpretacion"]
            print("Interpretación:", interpretacion["lluvia"], interpretacion["viento"], interpretacion["temperatura"])

    else:
        print(resultado)
    print("=" * 55)


def iniciar_menu(consultar):
    while True:
        print("\n=== PROYECTO ATD · CIRCUITO WTA ===")
        print("1. ¿Quién ganaría?")
        print("2. Infravaloradas y sobrevaloradas")
        print("3. Jugadoras que más mejoran")
        print("4. Mejores por superficie")
        print("5. Meteorología del torneo")
        print("6. Comprobar conexión / estado")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()
        if opcion == "0":
            print("¡Hasta pronto!")
            break
        try:
            peticion = pedir_peticion(opcion, consultar)
            print("\nConsultando datos...")
            respuesta = consultar(peticion)
            mostrar_resultado(peticion, respuesta)
        except (ValueError, OSError, ConnectionError, TimeoutError) as error:
            print("\nNo se ha podido completar la consulta:", error)


def consultar_servidor(peticion, host="127.0.0.1", puerto=5000):
    with socket.create_connection((host, puerto), timeout=15) as conexion:
        # Una extracción real de Selenium puede tardar varios minutos.
        conexion.settimeout(240)
        enviar_mensaje(conexion, peticion)
        return recibir_mensaje(conexion)


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description="Cliente TCP del proyecto ATD")
    argumentos.add_argument("--host", default="127.0.0.1")
    argumentos.add_argument("--puerto", type=int, default=5000)
    opciones = argumentos.parse_args()

    def enviar(peticion):
        return consultar_servidor(peticion, opciones.host, opciones.puerto)

    iniciar_menu(enviar)
