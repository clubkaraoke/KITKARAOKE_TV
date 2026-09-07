# FLUJO DEL CLIENTE · PRUEBA DEL SISTEMA

## Objetivo
Que un cliente pueda probar KITKARAOKE sin entender yt-dlp, FFmpeg, IPs o puertos.

## Flujo final propuesto
1. El cliente recibe un enlace de prueba de KITKARAOKE.
2. En la PC descarga/abre `KITKARAOKE DJ Trial` (el empaquetado se hará después).
3. En su Smart TV abre una sola dirección: `tv.kitkaraoke.com`.
4. La TV muestra un código de 4 dígitos, por ejemplo `4827`.
5. En KITKARAOKE DJ pulsa `VINCULAR TV`, escribe `4827` y asigna `TV SALA`.
6. La TV cambia a `TV CONECTADA`.
7. El cliente carga un CDP o busca una canción.
8. Reproduce y verifica video + audio.
9. Prueba logo, cumpleaños/aviso, AHORA CANTA y modo NEGRO/ESPERA.
10. Escanea el QR con un celular, envía un pedido y lo acepta desde el panel DJ.
11. Si algo falla, pulsa `LOGS`, copia o descarga el diagnóstico y lo envía a soporte.

## Qué debe sentir el cliente
- No escribe IP local.
- No abre puertos manualmente.
- No ve carpetas técnicas.
- No instala yt-dlp/FFmpeg por separado.
- La TV no muestra controles DJ.
- Si vuelve a usar la misma TV, el sistema debe poder recordarla.

## Prueba comercial futura
Podemos limitar la Trial por tiempo, número de canciones o funciones premium. Eso se definirá después de estabilizar web + vinculación.
