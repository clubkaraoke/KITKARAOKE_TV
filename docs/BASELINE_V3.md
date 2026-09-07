# BASELINE OFICIAL · KITKARAOKE

## Decisión de producto

La base oficial desde este punto es:

- Diseño maestro: web/DISEÑO_MAESTRO_FASE_2_1.html — debe respetarse visualmente tal cual salvo cambios aprobados explícitamente.
- Motor YouTube: KITKARAOKE QUEUE PLAYER V3, no V4/V5.2.
- Puerto original V3: 8769.

## Regla de no regresión

No modificar la estrategia de reproducción V3 mientras se integra la interfaz:

VIDEO_ID -> yt-dlp --get-url -> video/audio -> FFmpeg -> navegador local

El buscador V3 usa ytsearch local y no requiere YouTube Data API key.

## Funciones V3 que deben conservarse

- Abrir CDP.
- Buscar YouTube.
- Pegar URL/ID de YouTube.
- Agregar a cola.
- Reproducir ahora.
- Drag & drop de cola.
- Anterior/siguiente según el nuevo orden.
- Motor yt-dlp + Deno + FFmpeg.
- Diagnóstico YouTube real.

## Forma de trabajo

A partir de esta base, los cambios deben ser pequeños y comprobables. Primero se integra la UI exacta al motor V3. Después se agregan funciones una por una sin sustituir el resolver que ya funcionó en Windows.
