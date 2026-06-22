# Notas utiles - charly-tricks.dev

## Herramientas de Google

### Probar datos estructurados (en vivo)
https://search.google.com/test/rich-results
Pegar https://charly-tricks.dev y tocar "Probar URL".
Muestra lo que Google ve AHORA (no el reporte viejo de Search Console).
Debe detectar: Empresas locales, Organizacion, Fragmentos de resenas.
NO debe aparecer "Productos".

### Google Search Console
https://search.google.com/search-console
- Inspeccionar URL: pegar https://charly-tricks.dev y "Solicitar indexacion"
- Sirve para forzar que Google vuelva a rastrear

## Reglas importantes del schema (NO romper)

- NO marcar las uvas como "Product" / "hasOfferCatalog".
  La venta es en finca, sin envios, sin devoluciones, precio a convenir.
  Marcar productos obliga a inventar datos falsos (envio gratis, devolucion)
  y Google da errores de "Fragmentos de productos" y "Fichas de comerciantes".
- El schema correcto es solo: LocalBusiness + Person + Resenas reales.

## Favicon para Google

- Google exige favicon en MULTIPLOS DE 48: 48x48, 96x96, 144x144, 192x192.
- Un favicon 32x32 lo ignora y muestra el globo gris generico.
- Archivos en /var/www/vina-sanmartin/: favicon-48/96/144/192.png
- robots.txt debe permitir el acceso (Allow: /)
- Tras cambiar: purgar cache en Cloudflare + Solicitar indexacion.

## Cloudflare

- Panel: dash.cloudflare.com
- Bloquear bots de IA: dejar en "No bloquear (permitir rastreadores)"
  para no afectar el SEO ni el favicon de Google.
- Purgar cache: Almacenamiento en cache > Configuracion > Purgar todo

## Comandos utiles en el VPS

### Ver servicios corriendo
pm2 list

### Ver logs de un servicio
pm2 logs email-bot
pm2 logs reviews-api

### Reiniciar un servicio
pm2 restart email-bot

### Verificar favicon accesible
curl -skI https://127.0.0.1/favicon-96.png -H "Host: charly-tricks.dev" | head -1

### Probar nginx
nginx -t && systemctl reload nginx

## Backup en GitHub

cd /root/charly-tricks-project
# (copiar antes los archivos actualizados desde /var/www o los bots)
git add .
git commit -m "descripcion del cambio"
git push

## Servicios PM2 activos
- email-bot: responde emails con IA (Spacemail IMAP + DeepSeek + Resend)
- reviews-api: sistema de resenas con respuestas automaticas de IA

## PENDIENTE: Google AdSense (esperar ~2 semanas)

Fecha de lanzamiento web: 20 junio 2026
Solicitar AdSense aprox: a partir del 5 julio 2026

Prerequisitos (ya cumplidos):
- HTTPS, politica de privacidad, contenido original, contacto, Analytics

Por que esperar:
- AdSense rechaza sitios muy nuevos o con poco historial de trafico.
- Esperar 2-4 semanas da mas chances de aprobacion a la primera.

Como solicitar cuando llegue el momento:
- Entrar a https://www.google.com/adsense
- Agregar el sitio charly-tricks.dev
- Pegar el codigo que den en el <head> (igual que hicimos con Analytics)
- Esperar revision de Google (puede tardar dias o semanas)
