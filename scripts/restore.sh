#!/bin/bash
# restore.sh — Restauration de la base de données depuis un backup
# Usage: ./restore.sh <fichier_backup.dump.gz>
# Exemple: ./restore.sh /backups/dolibarr_20260501_020000.dump.gz

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 <fichier_backup.dump.gz>"
    echo ""
    echo "Backups disponibles:"
    ls -lh /backups/dolibarr/*.dump.gz 2>/dev/null || echo "  Aucun backup trouvé dans /backups/dolibarr/"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Fichier non trouvé: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ATTENTION: Cette opération va ÉCRASER la base de données actuelle."
echo "📁 Fichier de restauration: $BACKUP_FILE"
read -p "Confirmer la restauration? (oui/NON): " CONFIRM

if [ "$CONFIRM" != "oui" ]; then
    echo "❌ Restauration annulée."
    exit 0
fi

echo "🛑 Arrêt de Dolibarr..."
docker-compose stop dolibarr

echo "🗄️  Restauration de la base de données..."
docker exec immo-postgres psql -U dolibarr -c "DROP DATABASE dolibarr;"
docker exec immo-postgres psql -U dolibarr -c "CREATE DATABASE dolibarr OWNER dolibarr;"

gunzip -c "$BACKUP_FILE" | docker exec -i immo-postgres pg_restore -U dolibarr -d dolibarr -F c

echo "🚀 Redémarrage de Dolibarr..."
docker-compose start dolibarr

echo "✅ Restauration terminée."
