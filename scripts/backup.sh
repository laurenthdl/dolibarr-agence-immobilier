#!/bin/bash
# backup.sh — Sauvegarde automatisée Dolibarr + PostgreSQL + documents
# Usage: ./backup.sh [retention_days]
# Exemple: ./backup.sh 30

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups/dolibarr}"
RETENTION_DAYS="${1:-30}"
DATE=$(date +%Y%m%d_%H%M%S)
DOCKER_COMPOSE_DIR="${DOCKER_COMPOSE_DIR:-/opt/immobilier-ci}"
LOG_FILE="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"

log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S') $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

log "=== DÉBUT SAUVEGARDE $DATE ==="

# Sauvegarde PostgreSQL
log "Sauvegarde de la base de données..."
docker exec immo-postgres pg_dump -U dolibarr -d dolibarr -F c -f "/tmp/dolibarr_$DATE.dump"
docker cp "immo-postgres:/tmp/dolibarr_$DATE.dump" "$BACKUP_DIR/"
docker exec immo-postgres rm "/tmp/dolibarr_$DATE.dump"
gzip "$BACKUP_DIR/dolibarr_$DATE.dump"
log "✅ Base de données sauvegardée: dolibarr_$DATE.dump.gz"

# Sauvegarde des documents Dolibarr
log "Sauvegarde des documents..."
if [ -d "$DOCKER_COMPOSE_DIR/dolibarr_data" ]; then
    tar czf "$BACKUP_DIR/documents_$DATE.tar.gz" -C "$DOCKER_COMPOSE_DIR" dolibarr_data
    log "✅ Documents sauvegardés: documents_$DATE.tar.gz"
else
    log "⚠️  Volume documents non trouvé, sauvegarde via Docker..."
    docker run --rm -v gestion_agence_immo_dolibarr_data:/data \
        -v "$BACKUP_DIR:/backup" alpine tar czf "/backup/documents_$DATE.tar.gz" -C /data .
    log "✅ Documents sauvegardés via Docker"
fi

# Nettoyage des anciennes sauvegardes
log "Nettoyage des sauvegardes de plus de $RETENTION_DAYS jours..."
find "$BACKUP_DIR" -name "dolibarr_*.dump.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "documents_*.tar.gz" -mtime +$RETENTION_DAYS -delete
log "✅ Nettoyage terminé"

log "=== SAUVEGARDE TERMINÉE ==="
