#!/bin/bash
# healthcheck.sh — Vérification de santé des services immobiliers
# Usage: ./healthcheck.sh
# Retourne 0 si tout est OK, 1 sinon

EXIT_CODE=0

echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="

# Vérifier PostgreSQL
if docker exec immo-postgres pg_isready -U dolibarr >/dev/null 2>&1; then
    echo "✅ PostgreSQL : OK"
else
    echo "❌ PostgreSQL : DOWN"
    EXIT_CODE=1
fi

# Vérifier Dolibarr
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Dolibarr : OK (HTTP $HTTP_CODE)"
else
    echo "❌ Dolibarr : DOWN (HTTP $HTTP_CODE)"
    EXIT_CODE=1
fi

# Espace disque
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    echo "✅ Disque : ${DISK_USAGE}% utilisé"
else
    echo "⚠️  Disque : ${DISK_USAGE}% utilisé (ALERTE)"
    EXIT_CODE=1
fi

# Mémoire
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEMORY_USAGE" -lt 90 ]; then
    echo "✅ Mémoire : ${MEMORY_USAGE}% utilisée"
else
    echo "⚠️  Mémoire : ${MEMORY_USAGE}% utilisée (ALERTE)"
    EXIT_CODE=1
fi

# Tables immobilières
TABLE_COUNT=$(docker exec immo-postgres psql -U dolibarr -d dolibarr -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'llx_immo_%';" 2>/dev/null | xargs || echo 0)
if [ "$TABLE_COUNT" -gt 10 ]; then
    echo "✅ Tables immobilières : $TABLE_COUNT tables"
else
    echo "⚠️  Tables immobilières : seulement $TABLE_COUNT tables"
    EXIT_CODE=1
fi

exit $EXIT_CODE
