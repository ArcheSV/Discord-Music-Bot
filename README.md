
# 🎶 Bot de Música para Discord con Slash Commands

Este es un bot de música para Discord que utiliza `discord.py` (con la nueva implementación de `app_commands`), `yt_dlp` para la reproducción de audio desde YouTube y un sistema de búsqueda a través de la API de YouTube.

---

## Características principales

- **Reproducción de música** desde YouTube.
- **Búsqueda** de canciones usando la **API de YouTube**.
- **Cola de reproducción** para gestionar varias canciones.
- **Controles de reproducción** (pausar, reanudar, detener).
- **Desconexión por inactividad** tras 30 segundos si no hay nada reproduciéndose.
- **Interfaz con botones** para un uso más amigable.

---

## Requisitos

- Python 3.8 o superior.
- Un bot de Discord creado y con su **token** disponible.
- Una **API key de YouTube** (para que la búsqueda funcione).
- Librerías:
  - [discord.py](https://pypi.org/project/discord.py/) (versión compatible con `intents` y `app_commands`)
  - [yt_dlp](https://pypi.org/project/yt-dlp/)
  - [requests](https://pypi.org/project/requests/)
  - [asyncio](https://docs.python.org/3/library/asyncio.html)

Puedes instalar las dependencias con:

```bash
pip install discord.py yt_dlp requests
```

> **Nota:** Asegúrate de que tu versión de `discord.py` sea compatible con la implementación de aplicaciones (slash commands). Actualmente, el paquete recomendado es [py-cord](https://pypi.org/project/py-cord/) o [discord.py-self](https://pypi.org/project/discord.py-self/) si no tienes acceso a la antigua librería oficial.

---

## Configuración

1. Clona o descarga este repositorio.
2. Abre el archivo `.py` (donde se encuentra el código).
3. Reemplaza `"YT_API KEY"` por tu clave de **YouTube Data API** en la variable `YOUTUBE_API_KEY`.
4. Reemplaza `"DiscordToken"` con el token de tu bot en `bot.run("DiscordToken")`.

---

## Uso

Ejecuta el script con:

```bash
python bot.py
```

Observa en la consola si aparece el mensaje de que el bot está conectado.

En tu servidor de Discord:
- Usa el comando `/play <URL>` para **reproducir** la canción indicada o para **agregarla a la cola**.
- Usa el comando `/search <término>` para **buscar** canciones en YouTube. Selecciona en el menú desplegable la que desees.
- Controla la música con los **botones** que aparecen (Pausar, Reanudar, Detener).

> **IMPORTANTE:** Asegúrate de que tu bot tenga los **permisos de conexión y habla** en el canal de voz donde lo invoques.

---

## Comandos disponibles

- **`/play [URL]`**  
  Reproduce una canción desde la URL especificada (YouTube, preferiblemente).  
  Ejemplo: `/play https://www.youtube.com/watch?v=n-2GnXKvIOU`

- **`/search [término de búsqueda]`**  
  Realiza una búsqueda en YouTube y te muestra los resultados en un menú desplegable para que selecciones el que desees.  
  Ejemplo: `/search Despacito`

---

## Personalización

- **Tiempo de inactividad**: 30 segundos para la desconexión automática cuando no se está reproduciendo música.
- **Control de volumen**: Si deseas ajustar el volumen, puedes modificar los parámetros en `discord.FFmpegPCMAudio`.

---

## Créditos

- **discord.py** por su libreria
- **yt_dlp** por la capacidad de reproducir audio de YouTube.
- **YouTube Data API** para buscar y obtener metadatos de las canciones.
- **A ti** por probar mi primer bot en python.

---
