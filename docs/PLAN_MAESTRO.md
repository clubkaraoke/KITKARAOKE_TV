# PLAN MAESTRO · KITKARAOKE TV

Este documento fija lo acordado para no perder mejoras entre conversaciones.

## Dominios y entornos
- `tv1.kitkaraoke.com` = desarrollo / laboratorio / pruebas.
- `tv.kitkaraoke.com` = producción para clientes.
- Rama `desarrollo` = pruebas.
- Rama `main` = versión aprobada.
- Producción no debe cambiar por un simple commit de prueba.

## Arquitectura profesional
- GitHub: código, historial, ramas, workflows y releases.
- OVH: frontend de KITKARAOKE TV + API + WebSocket + señalización WebRTC + sesiones.
- Redis: códigos de vinculación y sesiones temporales.
- coturn/TURN: respaldo cuando una conexión WebRTC directa no sea posible.
- PC del DJ: motor local de reproducción. YouTube/yt-dlp/FFmpeg no deben ejecutarse en OVH como ruta principal.
- TV: receptor limpio, sin controles DJ.
- Neocities queda fuera de KITKARAOKE TV; puede seguir usándose para otras webs estáticas.

## Vinculación TV
1. La TV abre `tv.kitkaraoke.com`.
2. OVH genera un código temporal de 4 dígitos.
3. La PC escribe el código y solicita vinculación.
4. OVH valida el código, lo consume y enlaza PC + TV.
5. La TV queda recordada con un ID seguro.
6. En futuras sesiones puede aparecer como `TV SALA`, `TV ESCENARIO`, etc.
7. Debe existir opción Olvidar / Desvincular.
8. Los códigos deben expirar automáticamente; objetivo inicial: 5 minutos.
9. Debe soportarse más de una TV en una fase posterior.

## Salida TV
- Video limpio.
- Logo cargable PNG/JPG/WEBP.
- Logo movible, redimensionable, transparencia, bloqueo y posición persistente.
- Avisos / cumpleaños / publicidad.
- Texto, tamaño, color, fondo, transparencia, posición y bloqueo.
- Lower third: AHORA CANTA + nombre del cantante.
- QR para pedidos.
- Escenas rápidas: EN VIVO, NEGRO, ESPERA, PRUEBA TV, VIDEO LIMPIO.
- Todo cambio realizado en CONTROL debe reflejarse en TV.
- Watchdog/reconexión si la TV queda congelada o pierde la sesión.

## Cola y reproducción
- Abrir CDP.
- Buscar YouTube.
- Pegar URL de YouTube.
- Agregar a cola.
- Reproducir ahora.
- Eliminar.
- Anterior / siguiente.
- Drag & Drop real para reordenar.
- Reordenar sin cortar la canción actual.
- Mantener el motor local ya validado: yt-dlp --get-url + FFmpeg.

## Pedidos de clientes
- Página móvil de pedidos.
- QR visible en TV.
- Cliente busca canción y envía pedido.
- Panel PEDIDOS en el DJ.
- DJ puede ACEPTAR / AGREGAR A COLA / DESCARTAR.
- Estado del pedido en fase posterior.

## Diagnóstico y LOGS
Debe existir un botón visible `LOGS`.
Registrar con hora, nivel y categoría:
- inicio/cierre de aplicación;
- estado del motor;
- versiones yt-dlp / Deno / FFmpeg;
- búsqueda;
- resolver YouTube y cada intento;
- error_code exacto;
- inicio/fin/error FFmpeg;
- errores HTML5 video;
- errores JavaScript;
- conexión WebSocket;
- creación/expiración/uso de código;
- TV conectada/desconectada/reconectada;
- WebRTC ICE / conexión / fallback TURN;
- latencia/estado de red;
- pedidos QR;
- errores HTTP/API.
Funciones:
- filtro INFO/WARN/ERROR;
- actualizar;
- copiar;
- descargar TXT;
- limpiar;
- nunca guardar contraseñas, cookies, tokens ni URLs privadas de stream.

## Seguridad
- HTTPS y WSS obligatorios en producción.
- Secretos solo en GitHub Secrets / OVH, nunca en JS público.
- IDs de receptor aleatorios.
- códigos de un solo uso y expirables;
- rate limiting;
- sesiones expirables;
- validación de origen;
- logs sin credenciales.

## Etapas
### Fase actual
1. Terminar web.
2. Terminar UX de vinculación.
3. Diagnóstico de Smart TV.
4. Backend real en OVH para código de 4 dígitos.
5. WebSocket.
6. WebRTC + TURN de respaldo.
7. Probar en `tv1.kitkaraoke.com`.
8. Aprobar.
9. Pasar a `tv.kitkaraoke.com`.

### Después
- Empaquetar motor local en KITKARAOKE DJ.exe / instalador.
- actualizador automático;
- licencias/pruebas comerciales;
- múltiples TVs;
- pantalla exclusiva de cantante;
- administración remota.


## Panel universal del cliente
Arquitectura acordada:
- `panel.kitkaraoke.com` = panel privado del administrador/propietario. No se expone a clientes.
- `app1.kitkaraoke.com` = laboratorio del panel universal de clientes.
- `app.kitkaraoke.com` = panel universal de clientes en producción.
- `tv1.kitkaraoke.com` = laboratorio del receptor TV.
- `tv.kitkaraoke.com` = receptor TV de producción.

### Funciones ya implementadas en APP1
- activación por código/licencia;
- licencia almacenada con hash, no en texto plano;
- sesiones con cookie HttpOnly;
- límite de dispositivos por licencia;
- fecha de vencimiento y estado;
- Trial de 7 días solo para entorno APP1;
- panel de estado de licencia;
- vinculación real con código de 4 dígitos contra TV1;
- logs por licencia;
- cierre de sesión;
- base SQLite persistente en OVH para desarrollo;
- secreto/pepper generado localmente en OVH y fuera de GitHub.

### Flujo final del cliente
1. Cliente entra a `app.kitkaraoke.com`.
2. Introduce su licencia o accede con su cuenta/licencia.
3. El sistema valida plan, vigencia y dispositivos permitidos.
4. Cliente abre `tv.kitkaraoke.com` en la Smart TV.
5. TV muestra código de 4 dígitos.
6. Cliente introduce el código desde su panel universal.
7. OVH vincula APP + TV.
8. Después, el motor local KITKARAOKE DJ se integrará al panel para búsqueda, CDP, cola, overlays y reproducción.
9. Si algo falla, el cliente abre LOGS y puede enviar diagnóstico a soporte.

### Producción futura
El módulo de administración de licencias se integrará después en `panel.kitkaraoke.com`, sin mezclar el acceso privado del administrador con el acceso de los clientes.
