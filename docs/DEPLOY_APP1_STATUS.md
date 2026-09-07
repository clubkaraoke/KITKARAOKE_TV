# ESTADO REAL · APP1

Actualizado: 2026-09-07

## Ya montado en OVH
- Aplicación: `/opt/kitkaraoke-app1`
- Puerto interno: `127.0.0.1:8792`
- Contenedor: `kitkaraoke-app1-client`
- Nginx preparado para: `app1.kitkaraoke.com`
- Base persistente: SQLite en `/opt/kitkaraoke-app1/data`
- Secreto de licencias: generado directamente en OVH, fuera de GitHub.

## Pruebas reales aprobadas
- Health backend: PASS
- Nginx root: HTTP 200
- Nginx health: HTTP 200
- Crear Trial APP1: PASS
- Activar licencia: PASS
- Crear sesión: PASS
- Consultar licencia activa: PASS
- Vincular TV desde APP1 contra TV1: PASS
- Registrar y consultar LOGS: PASS
- Deploy final: PASS

## Separación de dominios
- `panel.kitkaraoke.com` = administración privada
- `app1.kitkaraoke.com` = cliente / laboratorio
- `app.kitkaraoke.com` = cliente / producción futura
- `tv1.kitkaraoke.com` = receptor TV / laboratorio
- `tv.kitkaraoke.com` = receptor TV / producción futura

## Pendiente para acceso público
Crear DNS para `app1` y `tv1` apuntando a la IP pública del OVH y después emitir certificados HTTPS.
