# KITKARAOKE TV

Base oficial del nuevo KITKARAOKE EVENT PLAYER.

## Decisión actual

- **Diseño maestro:** `web/DISEÑO_MAESTRO_FASE_2_1.html`
- **Motor YouTube:** **KITKARAOKE QUEUE PLAYER V3**
- **Puerto base V3:** `8769`

## Regla principal

La interfaz nueva se integra sobre el motor V3 probado. No se reemplaza el flujo de reproducción que ya funcionó en Windows:

`VIDEO_ID -> yt-dlp --get-url -> video/audio -> FFmpeg -> navegador local`

El buscador V3 usa `ytsearch` local y no necesita YouTube Data API key.

## Flujo de trabajo

- `main`: base aprobada y cambios incrementales.
- Cada cambio funcional debe conservar la reproducción YouTube V3.
- El diseño maestro solo cambia cuando se aprueba explícitamente.

## Estructura inicial

- `web/DISEÑO_MAESTRO_FASE_2_1.html` — referencia visual exacta.
- `engine_v3/` — documentos, scripts y manifiesto del motor V3.
- `docs/BASELINE_V3.md` — reglas de integración y no regresión.

## Importante sobre binarios

El paquete V3 contiene Deno, FFmpeg y yt-dlp. `deno.exe` pesa más de 100 MB, por encima del límite normal por archivo de GitHub. El archivo `engine_v3/ENGINE_MANIFEST.md` fija tamaños y SHA-256 exactos para no sustituir accidentalmente el motor probado.
