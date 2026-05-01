#!/bin/bash
# update.sh — Mise à jour des modules depuis Git
# Usage: ./update.sh [module_name]
# Exemple: ./update.sh immocore  (met à jour un seul module)
#          ./update.sh           (met à jour tous les modules)

set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/immobilier-ci}"
cd "$INSTALL_DIR"

MODULES=(
    "dolibarr-agence-immocore"
    "dolibarr-agence-immobien"
    "dolibarr-agence-immoclient"
    "dolibarr-agence-immolocatif"
    "dolibarr-agence-immovente"
    "dolibarr-agence-immoreno"
    "dolibarr-agence-immosyndic"
    "dolibarr-agence-immomarche"
    "dolibarr-agence-immodjamo"
    "dolibarr-agence-immorapports"
)

update_module() {
    local module="$1"
    echo "🔄 Mise à jour de $module..."
    if [ -d "$module/.git" ]; then
        (cd "$module" && git pull origin main)
        echo "✅ $module mis à jour"
    else
        echo "⚠️  $module n'est pas un repository git"
    fi
}

if [ $# -eq 1 ]; then
    # Vérifier si le nom contient le préfixe
    module_name="$1"
    if [[ ! "$module_name" == dolibarr-agence-* ]]; then
        module_name="dolibarr-agence-$module_name"
    fi
    update_module "$module_name"
else
    for module in "${MODULES[@]}"; do
        update_module "$module"
    done
fi

echo "🚀 Redémarrage de Dolibarr..."
docker-compose restart dolibarr

echo "✅ Mise à jour terminée."
