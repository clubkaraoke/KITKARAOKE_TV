# ESTADO REAL · TV1

Actualizado: 2026-09-07

## Ya montado en OVH
- Aplicación: `/opt/kitkaraoke-tv1`
- Puerto interno: `127.0.0.1:8791`
- Contenedor app: `kitkaraoke-tv1-app`
- Contenedor Redis: `kitkaraoke-tv1-redis`
- Nginx: virtual host `tv1.kitkaraoke.com`
- Backend: FastAPI
- Sesiones/códigos: Redis
- WebSocket receptor: `/ws/receiver/{receiverId}`
- Código de 4 dígitos: TTL 300 s
- Código: un solo uso

## Verificaciones aprobadas
- Health directo: PASS
- Health por Nginx usando Host tv1.kitkaraoke.com: HTTP 200
- Crear código: PASS
- Reclamar/vincular código: PASS
- Consultar estado paired: PASS
- Reutilizar el mismo código: bloqueado correctamente (404)
- Notificación de vinculación por WebSocket: PASS

## Pendiente externo
`tv1.kitkaraoke.com` todavía no existe en DNS público.

Hasta que DNS apunte a OVH:
- el servicio está funcionando dentro del VPS;
- Nginx ya sabe recibir `tv1.kitkaraoke.com`;
- no puede emitirse el certificado HTTPS público de tv1;
- una Smart TV fuera del VPS todavía no puede abrir el dominio.

### Registro DNS recomendado
Crear:
- Tipo: CNAME
- Host/Nombre: `tv1`
- Destino: `panel.kitkaraoke.com`

Después confirmar propagación y emitir Let's Encrypt para `tv1.kitkaraoke.com`.

## Próxima prueba
1. Abrir `https://tv1.kitkaraoke.com/tv` en un dispositivo.
2. Confirmar código de 4 dígitos.
3. Abrir `https://tv1.kitkaraoke.com/control` en otro dispositivo.
4. Vincular el código.
5. Confirmar cambio inmediato en la TV por WebSocket.
6. Probar Smart TV real y diagnóstico.
