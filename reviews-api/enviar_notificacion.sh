#!/bin/bash
# Uso: ./enviar_notificacion.sh "Título" "Mensaje"
TITULO="${1:-🍇 Viña San Martín}"
MENSAJE="${2:-¡Empezó la temporada de cosecha! Vení a buscar tu uva fresca.}"

curl -s -X POST http://127.0.0.1:5000/api/send-notification \
  -H "Content-Type: application/json" \
  -H "X-Secret: TU_SECRETO_ENVIO" \
  -d "{\"title\":\"$TITULO\",\"body\":\"$MENSAJE\",\"url\":\"https://charly-tricks.dev\"}"
echo ""
