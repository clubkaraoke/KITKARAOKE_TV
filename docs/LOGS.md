# CONTRATO DE LOGS

El botón LOGS será una herramienta de soporte, no una consola técnica confusa.

Formato recomendado:
`2026-09-07 00:15:03 | ERROR | RESOLVER | FORMAT_UNAVAILABLE | video=xxxxxxxxxxx`

Categorías mínimas:
APP, ENGINE, SEARCH, RESOLVER, FFMPEG, VIDEO, TV, WS, WEBRTC, TURN, NETWORK, REQUESTS, OVERLAY, API, BROWSER.

Cada error debe indicar:
- qué falló;
- en qué módulo;
- código de error;
- canción/video afectado cuando aplique;
- intento utilizado;
- acción sugerida cuando sea posible.

Nunca incluir:
- cookies;
- contraseñas;
- tokens;
- claves API;
- URL completa privada de stream.
