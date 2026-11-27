# Proyecto ATD — Cliente y servidor TCP

Versión simplificada: **solo hay dos archivos principales** (`cliente.py` y `servidor.py`). Las cinco funcionalidades del proyecto siguen en módulos Python independientes, que el servidor importa cuando los necesita.

## Estructura

- `cliente.py`: contiene el menú, pregunta las opciones al usuario, envía las peticiones y muestra los resultados.
- `servidor.py`: recibe peticiones por socket TCP, valida los parámetros, llama a los archivos de funciones y devuelve la respuesta.
- `predecir.py`, `predecir2.py`, `tabstract_ltennisGOOD.py`, `ranking.py`, `funcion_jugadoras.py`: análisis de datos de tenis.
- `tennis_abstract.py`, `livetennis.py`, `wta_weather.py`: obtención de datos en webs.
- `consulta_meteorologia.py`, `weatherAPI.py`: consulta e interpretación de condiciones históricas.

No hay `aplicacion.py`, `interfaz.py` ni `protocolo.py`. El menú que estaba en `interfaz.py` está dentro de `cliente.py`. El código que llamaba a las distintas funciones desde `aplicacion.py` está ahora en `servidor.py`. Las funciones de envío y recepción de TCP están integradas en ambos archivos.

## Cómo utilizarlo

Necesitas Python 3, Chrome instalado y conexión a Internet para las consultas de datos. Instala las dependencias desde esta misma carpeta:

```powershell
python -m pip install -r requirements.txt
```

Abre **dos terminales** en la carpeta del proyecto.

Terminal 1 — inicia el servidor:

```powershell
python servidor.py
```

Terminal 2 — abre el cliente:

```powershell
python cliente.py
```

Elige primero la opción `6. Comprobar conexión / estado`, que verifica la comunicación sin acceder a las webs. Después prueba las opciones del 1 al 5. El servidor mantiene las extracciones de datos en vivo; el cliente no hace scraping.

Para finalizar, pulsa `0` en el cliente y `Ctrl+C` en el servidor.

## Probar en dos ordenadores

Si están en la misma red local y se permite la conexión:

```powershell
# En el ordenador que aloja el servidor
python servidor.py --host 0.0.0.0 --puerto 5000

# En el ordenador cliente (IP privada de ejemplo)
python cliente.py --host 192.168.1.100 --puerto 5000
```

El protocolo transporta **JSON por socket TCP**, un objeto por línea, con respuesta `{"ok": true, "resultado": ...}` o `{"ok": false, "error": ...}`. No se crean CSV para transferir datos. Cada operación abre su propia conexión TCP.

**Aviso:** este prototipo no dispone de autenticación; no debe abrirse a Internet. Los scrapers pueden necesitar actualizaciones si las páginas cambian su HTML. La extracción semanal puede tardar; el servidor procesa una petición a la vez.
