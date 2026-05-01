#!/bin/bash
# install.sh — Script d'installation automatisée
# Gestion Agence Immobilière Côte d'Ivoire (Dolibarr 23.x)
# Usage: ./install.sh [OPTIONS]
# Options: --with-monitoring  (active Prometheus + Grafana)

set -euo pipefail

IFS=$'\n\t'

REPO_BASE="https://github.com/laurenthdl"
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

INSTALL_DIR="${INSTALL_DIR:-/opt/immobilier-ci}"
WITH_MONITORING=false
LOG_FILE="/tmp/immobilier-install-$(date +%Y%m%d-%H%M%S).log"


print_banner() {
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     GESTION AGENCE IMMOBILIERE — COTE D'IVOIRE                ║
║     Installation automatisée Dolibarr 23.x + Modules          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
}

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "INFO" "Vérification des prérequis..."

    local missing=()

    if ! command -v docker >/dev/null 2>&1; then
        missing+=("docker")
    fi

    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        missing+=("docker-compose")
    fi

    if ! command -v git >/dev/null 2>&1; then
        missing+=("git")
    fi

    if ! command -v curl >/dev/null 2>&1; then
        missing+=("curl")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log "ERROR" "Prérequis manquants: ${missing[*]}"
        log "INFO" "Installez-les avec:"
        log "INFO" "  sudo apt update"
        log "INFO" "  sudo apt install -y git curl docker.io docker-compose-plugin"
        log "INFO" "  sudo usermod -aG docker $USER"
        log "INFO" "  Puis déconnectez-vous et reconnectez-vous."
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        log "ERROR" "Docker est installé mais le service ne répond pas."
        log "INFO" "Lancez: sudo systemctl start docker"
        exit 1
    fi

    log "SUCCESS" "Tous les prérequis sont satisfaits."
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-monitoring)
                WITH_MONITORING=true
                shift
                ;;
            --dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --help|-h)
                cat << 'EOF'
Usage: ./install.sh [OPTIONS]

Options:
  --with-monitoring    Active Prometheus + Grafana (monitoring)
  --dir PATH           Répertoire d'installation (défaut: /opt/immobilier-ci)
  --help, -h           Affiche cette aide

Exemples:
  ./install.sh                              # Installation standard
  ./install.sh --with-monitoring            # Avec monitoring
  ./install.sh --dir /home/user/immo        # Répertoire personnalisé
EOF
                exit 0
                ;;
            *)
                log "ERROR" "Option inconnue: $1"
                log "INFO" "Utilisez --help pour voir les options disponibles."
                exit 1
                ;;
        esac
    done
}

clone_repositories() {
    log "INFO" "Clonage des modules dans $INSTALL_DIR..."

    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"

    for module in "${MODULES[@]}"; do
        if [ -d "$module/.git" ]; then
            log "INFO" "  $module existe déjà, mise à jour..."
            (cd "$module" && git pull origin main) || log "WARN" "  Échec du pull pour $module"
        else
            log "INFO" "  Clonage $module..."
            git clone "${REPO_BASE}/${module}.git" || {
                log "ERROR" "  Échec du clonage de $module"
                exit 1
            }
        fi
    done

    log "SUCCESS" "Tous les modules sont à jour."
}

create_docker_compose() {
    log "INFO" "Création du fichier docker-compose.yml..."

    cat > "$INSTALL_DIR/docker-compose.yml" << 'DOCKERCOMPOSE'
version: "3.8"

services:
  db:
    image: postgres:15
    container_name: immo-postgres
    environment:
      POSTGRES_USER: dolibarr
      POSTGRES_PASSWORD: dolibarr
      POSTGRES_DB: dolibarr
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"
    networks:
      - immo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dolibarr"]
      interval: 10s
      timeout: 5s
      retries: 5

  dolibarr:
    image: dolibarr/dolibarr:23.0.2
    container_name: immo-dolibarr
    environment:
      DOLI_DB_HOST: db
      DOLI_DB_NAME: dolibarr
      DOLI_DB_USER: dolibarr
      DOLI_DB_PASSWORD: dolibarr
      DOLI_DB_TYPE: pgsql
      DOLI_URL_ROOT: http://localhost:8080
      DOLI_ADMIN_LOGIN: admin
      DOLI_ADMIN_PASSWORD: admin
    volumes:
      - dolibarr_data:/var/www/html/documents
      - ./dolibarr-agence-immocore:/var/www/html/custom/immocore:ro
      - ./dolibarr-agence-immobien:/var/www/html/custom/immobien:ro
      - ./dolibarr-agence-immoclient:/var/www/html/custom/immoclient:ro
      - ./dolibarr-agence-immolocatif:/var/www/html/custom/immolocatif:ro
      - ./dolibarr-agence-immovente:/var/www/html/custom/immovente:ro
      - ./dolibarr-agence-immoreno:/var/www/html/custom/immoreno:ro
      - ./dolibarr-agence-immosyndic:/var/www/html/custom/immosyndic:ro
      - ./dolibarr-agence-immomarche:/var/www/html/custom/immomarche:ro
      - ./dolibarr-agence-immodjamo:/var/www/html/custom/immodjamo:ro
      - ./dolibarr-agence-immorapports:/var/www/html/custom/immorapports:ro
    ports:
      - "8080:80"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - immo-network
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: immo-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@localhost.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "8081:80"
    depends_on:
      - db
    networks:
      - immo-network

volumes:
  postgres_data:
  dolibarr_data:

networks:
  immo-network:
    driver: bridge
DOCKERCOMPOSE

    if [ "$WITH_MONITORING" = true ]; then
        log "INFO" "Ajout des services de monitoring..."
        cat >> "$INSTALL_DIR/docker-compose.yml" << 'MONITORING'

  prometheus:
    image: prom/prometheus:latest
    container_name: immo-prometheus
    volumes:
      - ./scripts/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - immo-network

  grafana:
    image: grafana/grafana:latest
    container_name: immo-grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - immo-network

volumes:
  prometheus_data:
  grafana_data:
MONITORING

        # Créer prometheus.yml
        mkdir -p "$INSTALL_DIR/scripts"
        cat > "$INSTALL_DIR/scripts/prometheus.yml" << 'PROMETHEUS'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
  - job_name: 'dolibarr'
    static_configs:
      - targets: ['dolibarr:80']
PROMETHEUS
    fi

    log "SUCCESS" "docker-compose.yml créé."
}

create_init_sql() {
    log "INFO" "Création du script SQL d'initialisation..."

    mkdir -p "$INSTALL_DIR/scripts"

    cat > "$INSTALL_DIR/scripts/init.sql" << 'SQLINIT'
-- Initialisation des modules immobiliers
-- Exécuté automatiquement au premier démarrage de PostgreSQL

\echo 'Création des tables immobilières...'

-- Core: table de configuration
CREATE TABLE IF NOT EXISTS llx_immo_config (
    rowid serial PRIMARY KEY,
    cle varchar(64) NOT NULL UNIQUE,
    valeur text,
    description varchar(255)
);

-- Immobien
\i /docker-entrypoint-initdb.d/llx_immo_bien.sql

-- Immolocatif
\i /docker-entrypoint-initdb.d/llx_immo_bail.sql

-- Immovente
\i /docker-entrypoint-initdb.d/llx_immo_mandat_vente.sql

-- Immoreno
\i /docker-entrypoint-initdb.d/llx_immo_reno.sql

-- Immosyndic
\i /docker-entrypoint-initdb.d/llx_immo_syndic.sql

-- Immomarche
\i /docker-entrypoint-initdb.d/llx_immo_marche.sql

-- Imodjamo
\i /docker-entrypoint-initdb.d/llx_immo_paiement_mobile.sql

-- Immorapports
\i /docker-entrypoint-initdb.d/llx_immo_rapport.sql

-- Catalogue: types de bien
CREATE TABLE IF NOT EXISTS llx_immo_type_bien (
    rowid serial PRIMARY KEY,
    code varchar(32) NOT NULL UNIQUE,
    label varchar(128) NOT NULL,
    actif integer DEFAULT 1
);
INSERT INTO llx_immo_type_bien (code, label) VALUES
('MAISON', 'Maison individuelle'),
('APPART', 'Appartement'),
('BUREAU', 'Bureau'),
('BOUTIQUE', 'Boutique / Commerce'),
('ENTREPOT', 'Entrepôt / Hangar'),
('TERRAIN', 'Terrain nu'),
('IMMEUBLE', 'Immeuble complet')
ON CONFLICT (code) DO NOTHING;

-- Catalogue: états de bien
CREATE TABLE IF NOT EXISTS llx_immo_etat_bien (
    rowid serial PRIMARY KEY,
    code varchar(32) NOT NULL UNIQUE,
    label varchar(128) NOT NULL,
    couleur varchar(7) DEFAULT '#CCCCCC',
    actif integer DEFAULT 1
);
INSERT INTO llx_immo_etat_bien (code, label, couleur) VALUES
('A_ACQUERIR', 'À acquérir', '#999999'),
('DISPONIBLE', 'Disponible', '#00AA00'),
('A_LOUER', 'À louer', '#0066CC'),
('LOUE', 'Loué', '#00CC00'),
('A_VENDRE', 'À vendre', '#FF6600'),
('VENDU', 'Vendu', '#CC0000'),
('RENOVATION', 'En rénovation', '#FFCC00'),
('ARCHIVE', 'Archivé', '#333333')
ON CONFLICT (code) DO NOTHING;

-- Catalogue: types de bail
CREATE TABLE IF NOT EXISTS llx_immo_type_bail (
    rowid serial PRIMARY KEY,
    code varchar(32) NOT NULL UNIQUE,
    label varchar(128) NOT NULL,
    duree_defaut_mois integer,
    actif integer DEFAULT 1
);
INSERT INTO llx_immo_type_bail (code, label, duree_defaut_mois) VALUES
('RES_VIDE', 'Résidentiel vide', 12),
('RES_MEUBLE', 'Résidentiel meublé', 6),
('COMMERCIAL', 'Commercial', 36),
('PROFESSIONNEL', 'Professionnel', 36),
('SAISONNIER', 'Saisonnier', 3)
ON CONFLICT (code) DO NOTHING;

-- Catalogue: types de client
CREATE TABLE IF NOT EXISTS llx_immo_type_client (
    rowid serial PRIMARY KEY,
    code varchar(32) NOT NULL UNIQUE,
    label varchar(128) NOT NULL,
    actif integer DEFAULT 1
);
INSERT INTO llx_immo_type_client (code, label) VALUES
('PROPRIETAIRE', 'Propriétaire'),
('LOCATAIRE', 'Locataire'),
('ACHETEUR', 'Acheteur'),
('PROSPECT', 'Prospect'),
('BAILLEUR', 'Bailleur'),
('SYNDIC', 'Syndic')
ON CONFLICT (code) DO NOTHING;

-- Catalogue: modes de paiement
CREATE TABLE IF NOT EXISTS llx_immo_mode_paiement (
    rowid serial PRIMARY KEY,
    code varchar(32) NOT NULL UNIQUE,
    label varchar(128) NOT NULL,
    actif integer DEFAULT 1
);
INSERT INTO llx_immo_mode_paiement (code, label) VALUES
('ESPECES', 'Espèces'),
('VIREMENT', 'Virement bancaire'),
('CHEQUE', 'Chèque'),
('DJAMO', 'Djamo'),
('OM', 'Orange Money'),
('MTN', 'MTN Mobile Money')
ON CONFLICT (code) DO NOTHING;

-- Historique
CREATE TABLE IF NOT EXISTS llx_immo_history (
    rowid serial PRIMARY KEY,
    fk_element integer,
    element_type varchar(64),
    action varchar(64),
    champ varchar(64),
    ancienne_valeur text,
    nouvelle_valeur text,
    fk_user integer,
    datec timestamp DEFAULT CURRENT_TIMESTAMP
);

\echo 'Initialisation terminée avec succès.'
SQLINIT

    log "SUCCESS" "Script SQL d'initialisation créé."
}

copy_sql_files() {
    log "INFO" "Copie des fichiers SQL des modules..."

    for module in "${MODULES[@]}"; do
        if [ -d "$INSTALL_DIR/$module/sql" ]; then
            cp "$INSTALL_DIR/$module/sql/"*.sql "$INSTALL_DIR/scripts/" 2>/dev/null || true
            log "INFO" "  SQL copiés depuis $module"
        fi
    done

    log "SUCCESS" "Fichiers SQL copiés."
}

launch_infrastructure() {
    log "INFO" "Démarrage de l'infrastructure Docker..."

    cd "$INSTALL_DIR"

    log "INFO" "  Téléchargement des images (peut prendre plusieurs minutes)..."
    docker-compose pull

    log "INFO" "  Démarrage des conteneurs..."
    docker-compose up -d

    log "INFO" "  Attente de l'initialisation de la base de données..."
    sleep 10

    local retries=30
    while [ $retries -gt 0 ]; do
        if docker exec immo-postgres pg_isready -U dolibarr >/dev/null 2>&1; then
            log "SUCCESS" "PostgreSQL est prêt."
            break
        fi
        log "INFO" "  En attente de PostgreSQL... ($retries tentatives restantes)"
        sleep 5
        retries=$((retries - 1))
    done

    if [ $retries -eq 0 ]; then
        log "ERROR" "PostgreSQL n'a pas démarré dans le temps imparti."
        log "INFO" "Vérifiez les logs: docker logs immo-postgres"
        exit 1
    fi
}

verify_installation() {
    log "INFO" "Vérification de l'installation..."

    # Vérifier Dolibarr
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ || echo "000")
    if [ "$http_code" = "200" ] || [ "$http_code" = "302" ]; then
        log "SUCCESS" "Dolibarr répond (HTTP $http_code)."
    else
        log "WARN" "Dolibarr ne répond pas encore (HTTP $http_code). L'installation web est peut-être en cours."
    fi

    # Vérifier les tables
    local table_count
    table_count=$(docker exec immo-postgres psql -U dolibarr -d dolibarr -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'llx_immo_%';" 2>/dev/null | xargs)
    if [ "${table_count:-0}" -gt 0 ]; then
        log "SUCCESS" "$table_count tables immobilières trouvées."
    else
        log "WARN" "Aucune table immobilière trouvée. L'initialisation SQL peut être en cours."
    fi

    log "SUCCESS" "Vérification terminée."
}

print_summary() {
    cat << EOF

╔═══════════════════════════════════════════════════════════════╗
║                  INSTALLATION TERMINÉE                        ║
╚═══════════════════════════════════════════════════════════════╝

📁 Répertoire d'installation : $INSTALL_DIR
📝 Fichier de log : $LOG_FILE

🔗 Accès aux services :
   • Dolibarr ERP      : http://localhost:8080
   • pgAdmin (BDD)     : http://localhost:8081
                         admin@localhost.com / admin
EOF

    if [ "$WITH_MONITORING" = true ]; then
        cat << EOF
   • Prometheus        : http://localhost:9090
   • Grafana           : http://localhost:3000
EOF
    fi

cat << EOF

⚙️ Prochaines étapes :
   1. Finaliser l'installation Dolibarr :
      http://localhost:8080/install/
      → Sélectionner Français → Tester la connexion PostgreSQL
      → Créer le compte administrateur

   2. Activer les modules immobiliers :
      Configuration > Modules/Applications > Immobilier
      → Activer dans cet ordre : immocore → immobien → immoclient → immolocatif

   3. Configurer les catalogues :
      Immobilier > Configuration > Catalogues
      (les valeurs par défaut sont déjà peuplées)

   4. Consulter la documentation :
      $INSTALL_DIR/dolibarr-agence-immocore/docs/

📦 Commandes utiles :
   cd $INSTALL_DIR
   docker-compose ps              # Voir l'état des conteneurs
   docker-compose logs -f         # Voir les logs en temps réel
   docker-compose down            # Arrêter l'infrastructure
   docker-compose up -d           # Redémarrer

EOF
}

main() {
    print_banner
    parse_args "$@"
    check_prerequisites
    clone_repositories
    create_docker_compose
    create_init_sql
    copy_sql_files
    launch_infrastructure
    verify_installation
    print_summary
}

main "$@"
