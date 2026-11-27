"""Servidor TCP del proyecto ATD. Ejecutar: python servidor.py"""

import argparse
import json
import socket

"""Punto central de las cinco funcionalidades del proyecto ATD.

Puede usarse directamente (python aplicacion.py) o importarse desde servidor.py.
"""


def entero(valor, nombre, minimo, maximo):
    try:
        numero = int(valor)
    except (ValueError, TypeError):
        raise ValueError(nombre + " debe ser un número entero")
    if not minimo <= numero <= maximo:
        raise ValueError(nombre + " debe estar entre " + str(minimo) + " y " + str(maximo))
    return numero


def ejecutar_consulta(operacion, parametros=None):
    if parametros is None:
        parametros = {}
    if not isinstance(parametros, dict):
        raise ValueError("Los parámetros deben enviarse como un diccionario")

    if operacion == "estado":
        return {"mensaje": "Aplicación ATD operativa", "funcionalidades": 5}

    if operacion == "predecir_partido":
        from predecir import predecir_partido
        nombre1 = str(parametros.get("jugadora1", "")).strip()
        nombre2 = str(parametros.get("jugadora2", "")).strip()
        superficie = str(parametros.get("superficie", "")).strip().lower()
        if not nombre1 or not nombre2:
            raise ValueError("Debes indicar los nombres de las dos jugadoras")
        if superficie not in ("elo", "dura", "arcilla", "hierba"):
            raise ValueError("Superficie no válida: elo, dura, arcilla o hierba")
        resultado = predecir_partido(nombre1, nombre2, superficie)
        if isinstance(resultado, str):
            raise ValueError(resultado)
        return resultado

    if operacion == "comparar_jugadoras":
        from predecir2 import comparar_jugadoras
        nombre1 = str(parametros.get("jugadora1", "")).strip()
        nombre2 = str(parametros.get("jugadora2", "")).strip()
        if not nombre1 or not nombre2:
            raise ValueError("Debes indicar los nombres de las dos jugadoras")
        resultado = comparar_jugadoras(nombre1, nombre2)
        if isinstance(resultado, str):
            raise ValueError(resultado)
        return {"jugadora1": nombre1, "jugadora2": nombre2, "superficies": resultado}

    if operacion == "comparar_rankings":
        from tabstract_ltennisGOOD import comparar_rankings
        cantidad = entero(parametros.get("cantidad", 10), "Cantidad", 1, 30)
        top = entero(parametros.get("top", 100), "Top WTA", 1, 300)
        return comparar_rankings(cantidad, top)

    if operacion == "cambios_ranking":
        from ranking import cambios_ranking
        cantidad = entero(parametros.get("cantidad", 10), "Cantidad", 1, 20)
        return cambios_ranking(cantidad, 300)

    if operacion == "mejores_superficie":
        from funcion_jugadoras import mejores_superficie
        superficie = str(parametros.get("superficie", "")).strip().lower()
        cantidad = entero(parametros.get("cantidad", 10), "Cantidad", 1, 100)
        if superficie not in ("dura", "arcilla", "hierba"):
            raise ValueError("Elige dura, arcilla o hierba")
        return mejores_superficie(superficie, cantidad)

    if operacion == "listar_torneos":
        from wta_weather import listar_torneos
        return listar_torneos()

    if operacion == "meteorologia_torneo":
        from consulta_meteorologia import meteorologia_torneo
        nombres = parametros.get("torneos", [])
        if isinstance(nombres, str):
            nombres = [nombres]
        if not isinstance(nombres, list) or not 1 <= len(nombres) <= 5:
            raise ValueError("Debes seleccionar entre 1 y 5 torneos")
        for nombre in nombres:
            if not isinstance(nombre, str) or not nombre.strip():
                raise ValueError("Los nombres de los torneos deben ser textos no vacíos")
        cantidad_anios = entero(parametros.get("anios", 3), "Años históricos", 1, 5)
        resultado = meteorologia_torneo(nombres, cantidad_anios)
        if not resultado:
            raise ValueError("No se ha encontrado ninguno de los torneos solicitados")
        return resultado

    raise ValueError("Operación desconocida: " + str(operacion))


def procesar_peticion(peticion):
    """Da el mismo formato de respuesta a la aplicación local y al servidor."""
    try:
        if not isinstance(peticion, dict):
            raise ValueError("La petición debe ser un diccionario")
        resultado = ejecutar_consulta(peticion.get("operacion"), peticion.get("parametros"))
        return {"ok": True, "resultado": resultado}
    except Exception as error:
        return {"ok": False, "error": str(error)}


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


def atender_cliente(conexion, direccion=None):
    with conexion:
        conexion.settimeout(240)
        try:
            peticion = recibir_mensaje(conexion)
            if isinstance(peticion, dict):
                print("Consulta recibida:", peticion.get("operacion"), flush=True)
            respuesta = procesar_peticion(peticion)
        except Exception as error:
            respuesta = {"ok": False, "error": str(error)}
        try:
            enviar_mensaje(conexion, respuesta)
        except OSError as error:
            print("No se pudo enviar la respuesta:", error)


def iniciar_servidor(host="127.0.0.1", puerto=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, puerto))
        servidor.listen(5)
        print("Servidor ATD escuchando en", host + ":" + str(puerto))
        print("Pulsa Ctrl+C para detenerlo.")
        try:
            while True:
                conexion, direccion = servidor.accept()
                print("Cliente conectado:", direccion)
                atender_cliente(conexion, direccion)
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description="Servidor TCP del proyecto ATD")
    argumentos.add_argument("--host", default="127.0.0.1")
    argumentos.add_argument("--puerto", type=int, default=5000)
    opciones = argumentos.parse_args()
    iniciar_servidor(opciones.host, opciones.puerto)
