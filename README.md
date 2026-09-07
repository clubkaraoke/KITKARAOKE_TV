# KITKARAOKE TV

Proyecto para la salida de TV y vinculación remota de KITKARAOKE.

## Entornos
- `desarrollo` → **tv1.kitkaraoke.com** (laboratorio/pruebas).
- `main` → **tv.kitkaraoke.com** (producción aprobada).

## Arquitectura acordada
- GitHub: código, ramas, historial y despliegues.
- OVH: web + backend de vinculación + WebSocket + señalización WebRTC + TURN de respaldo.
- PC del DJ: motor local yt-dlp/FFmpeg.
- Smart TV: receptor limpio.
- Neocities no forma parte de KITKARAOKE TV.

## Objetivo de esta fase
1. Terminar la web del receptor TV.
2. Terminar la vinculación por código de 4 dígitos.
3. Crear diagnóstico de Smart TV.
4. Crear logs de soporte.
5. Probar todo primero en `tv1.kitkaraoke.com`.
6. Solo después pasar la versión aprobada a `tv.kitkaraoke.com`.

## Documentación
- `docs/PLAN_MAESTRO.md` — todas las mejoras acordadas.
- `docs/FLUJO_CLIENTE_PRUEBA.md` — experiencia de un cliente que prueba el sistema.
- `docs/LOGS.md` — qué debe registrar el sistema y qué nunca debe guardar.

> El motor local yt-dlp/FFmpeg no forma parte del frontend web y no debe moverse a OVH como ruta principal de reproducción.
