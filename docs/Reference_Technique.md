# Référence Technique — Gestion Agence Immobilière Côte d'Ivoire

> Version 1.0 | Dolibarr 23.x | Modules `700000` — `700009`
> **Public cible** : Ingénieurs système, Développeurs, Intégrateurs, Administrateurs avancés

---

## Table des matières

1. [Architecture et modules](#1-architecture-et-modules)
2. [Schéma de données](#2-schéma-de-données)
3. [Numérotation et référencement](#3-numérotation-et-référencement)
4. [Spécificités fiscales — Côte d'Ivoire](#4-spécificités-fiscales--côte-divoire)
5. [API REST](#5-api-rest)
6. [Sauvegarde et restauration](#6-sauvegarde-et-restauration)
7. [Migration](#7-migration)
8. [Troubleshooting](#8-troubleshooting)
9. [Monitoring](#9-monitoring)
10. [Support et ressources](#10-support-et-ressources)

---

## 1. Architecture et modules

### 1.1 Table des modules

| # | Module | Numéro | Dépendances directes | Phase |
|---|--------|--------|----------------------|-------|
| 1 | **immocore** | 700000 | Aucune | Core |
| 2 | **immobien** | 700001 | immocore | MVP |
| 3 | **immoclient** | 700002 | immocore | MVP |
| 4 | **immolocatif** | 700003 | immocore, immobien, immoclient | MVP |
| 5 | **immovente** | 700004 | immocore, immobien, immoclient | MVP |
| 6 | **immoreno** | 700005 | immocore, immobien | Extension |
| 7 | **immosyndic** | 700006 | immocore | Extension |
| 8 | **immomarche** | 700007 | immocore | Extension |
| 9 | **immodjamo** | 700008 | immocore, immolocatif | Extension |
| 10 | **immorapports** | 700009 | immocore, tous les autres | Extension |

### 1.2 Dépendances Docker

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   pgAdmin   │────▶│  PostgreSQL │◀────│   Dolibarr  │
│   :8081     │     │   :5432     │     │   :8080     │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                         ┌──────┴──────┐
                                         │  10 modules │
                                         │   custom/    │
                                         └─────────────┘
```

### 1.3 Points d'entrée web

| Service | URL | Identifiants par défaut |
|---------|-----|-------------------------|
| Dolibarr | `http://localhost:8080` | admin / admin |
| pgAdmin | `http://localhost:8081` | admin@localhost.com / admin |
| PostgreSQL | `localhost:5432` | dolibarr / dolibarr |

---

## 2. Schéma de données

### 2.1 Tables principales

| Table | Module | Description | Clés |
|-------|--------|-------------|------|
| `llx_immo_config` | Core | Paramètres globaux key-value | `cle` (unique) |
| `llx_immo_bien` | Bien | Fiches des biens immobiliers | `ref` (unique) |
| `llx_immo_bail` | Locatif | Contrats de location | `ref` (unique), FK `fk_bien`, `fk_locataire` |
| `llx_immo_quittance` | Locatif | Quittances mensuelles | `ref` (unique), FK `fk_bail` |
| `llx_immo_mandat_vente` | Vente | Mandats de vente | `ref` (unique), FK `fk_bien` |
| `llx_immo_compromis` | Vente | Promesses de vente | `ref` (unique), FK `fk_mandat` |
| `llx_immo_reno` | Reno | Travaux de rénovation | `ref` (unique), FK `fk_bien` |
| `llx_immo_syndic` | Syndic | Immeubles en copropriété | `ref` (unique) |
| `llx_immo_syndic_lot` | Syndic | Lots/appartements | `ref` (unique), FK `fk_syndic` |
| `llx_immo_syndic_charge` | Syndic | Charges de copropriété | `ref` (unique), FK `fk_syndic` |
| `llx_immo_syndic_paiement` | Syndic | Paiements de charges | FK `fk_charge`, `fk_lot` |
| `llx_immo_vente_comp` | Marché | Ventes comparables | `ref` (unique) |
| `llx_immo_location_comp` | Marché | Locations comparables | `ref` (unique) |
| `llx_immo_paiement_mobile` | Djamo | Transactions Djamo | `ref` (unique), FK `fk_bail` |
| `llx_immo_rapport_config` | Rapports | Configuration rapports | `ref` (unique) |

### 2.2 Tables de catalogue (Core)

| Table | Contenu | Peuplée à l'activation |
|-------|---------|------------------------|
| `llx_immo_type_bien` | Maison, Appartement, Bureau... | Oui |
| `llx_immo_etat_bien` | Disponible, Loué, Vendu... | Oui |
| `llx_immo_type_bail` | Résidentiel, Commercial... | Oui |
| `llx_immo_type_client` | Propriétaire, Locataire... | Oui |
| `llx_immo_mode_paiement` | Espèces, Virement, Djamo... | Oui |

### 2.3 Table d'historique (Core)

`llx_immo_history` : journal d'audit des changements d'état.

| Champ | Type | Description |
|-------|------|-------------|
| `rowid` | SERIAL PK | ID |
| `fk_element` | INTEGER | ID de l'élément modifié |
| `element_type` | VARCHAR(64) | Type (bien, bail, mandat...) |
| `action` | VARCHAR(64) | create, update, status_change |
| `champ` | VARCHAR(64) | Champ modifié |
| `ancienne_valeur` | TEXT | Valeur avant |
| `nouvelle_valeur` | TEXT | Valeur après |
| `fk_user` | INTEGER | Utilisateur ayant fait l'action |
| `datec` | TIMESTAMP | Date de l'action |

---

## 3. Numérotation et référencement

### 3.1 Formats de référence automatique

| Élément | Format PHP | Exemple |
|---------|------------|---------|
| Bien | `sprintf('B%04d-%04d', $year, $num)` | `B2026-0042` |
| Bail | `sprintf('BL%04d-%04d', $year, $num)` | `BL2026-0015` |
| Quittance | `sprintf('Q%04d-%05d', $year, $num)` | `Q2026-00042` |
| Mandat vente | `sprintf('MV%04d-%04d', $year, $num)` | `MV2026-0012` |
| Fiche travaux | `sprintf('RNO%04d-%04d', $year, $num)` | `RNO2026-0003` |
| Copropriété | `sprintf('SYD%04d-%04d', $year, $num)` | `SYD2026-0001` |
| Transaction Djamo | `sprintf('DJA%04d-%04d', $year, $num)` | `DJA2026-0045` |
| Rapport | `sprintf('RPT%04d-%04d', $year, $num)` | `RPT2026-0007` |

### 3.2 Logique d'incrément

La numérotation utilise le format `PREFIXE-ANNEE-SEQUENCE` :

```php
protected function getMaxNumRef(): int
{
    $sql = "SELECT MAX(CAST(SUBSTRING(ref FROM '-[0-9]+-([0-9]+)$') AS INTEGER)) as maxref";
    $sql .= " FROM ".$this->db->prefix().$this->table_element;
    // ...
}
```

> **Règle** : La séquence est réinitialisée à 1 chaque année civile. Les références contiennent l'année pour garantir l'unicité et faciliter l'archivage comptable.

---

## 4. Spécificités fiscales — Côte d'Ivoire

### 4.1 Taxe Locale sur la Propriété et la Publicité (TLPPU)

| Aspect | Détail |
|--------|--------|
| **Assiette** | Loyer annuel net (hors charges) |
| **Taux** | 11% à 20% selon la commune |
| **Calcul mensuel** | `TLPPU = Loyer mensuel × Taux communal / 100` |
| **Collecte** | Par l'agence et reversement aux collectivités |

**Taux indicatifs par commune** :

| Commune | Taux indicatif | Configuration recommandée |
|---------|----------------|---------------------------|
| Abidjan (Cocody, Plateau) | 18-20% | `IMMO_TAUX_TLPPU_DEFAUT = 18.00` |
| Abidjan (autres communes) | 15-18% | `IMMO_TAUX_TLPPU_DEFAUT = 15.00` |
| Bouaké, Yamoussoukro | 12-15% | `IMMO_TAUX_TLPPU_DEFAUT = 12.00` |
| Autres villes | 11-13% | `IMMO_TAUX_TLPPU_DEFAUT = 11.00` |

> Le taux peut être **surchargé par bien** via le champ `taux_tlppu` de la table `llx_immo_bien`. Si vide, c'est la valeur par défaut de la configuration qui s'applique.

### 4.2 Frais d'enregistrement des baux

| Durée du bail | Taux | Application |
|---------------|------|-------------|
| ≤ 1 an | Exempté | Baux courte durée |
| > 1 an | 6% du loyer global | Baux résidentiels longs, commerciaux |

Ce frais est affiché à titre informatif sur la fiche bail et le compromis de vente.

### 4.3 TVA sur vente immobilière

| Type de bien | TVA | Application |
|--------------|-----|-------------|
| Construction neuve | 18% du prix | Payée par l'acheteur |
| Ancien / Réhabilité | Exonéré | Sous conditions |

### 4.4 Commissions d'agence

| Type de transaction | Commission standard | Payée par |
|---------------------|---------------------|-----------|
| Vente | 5% à 10% du prix | Vendeur |
| Location | 1 à 2 mois de loyer | Propriétaire |

> Les commissions sont configurables par mandat via les champs `commission_type` et `commission_valeur`.

---

## 5. API REST

> **Statut** : Prévisionnel. Ces endpoints seront implémentés dans une version ultérieure.

### 5.1 Configuration

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/api/immo/config` | Lire la configuration globale | API Key |
| PUT | `/api/immo/config` | Modifier un paramètre | API Key + Admin |

### 5.2 Gestion locative

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/api/immo/baux` | Liste des baux (filtrable) | API Key |
| POST | `/api/immo/baux` | Créer un bail | API Key |
| GET | `/api/immo/baux/{id}` | Détail d'un bail | API Key |
| PUT | `/api/immo/baux/{id}` | Modifier un bail | API Key |
| GET | `/api/immo/baux/{id}/quittances` | Quittances du bail | API Key |
| POST | `/api/immo/baux/{id}/quittances` | Générer quittance | API Key |
| POST | `/api/immo/quittances/{id}/paiement` | Enregistrer paiement | API Key |
| GET | `/api/immo/echeancier` | Échéancier global | API Key |

### 5.3 Vente

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/api/immo/mandats` | Liste des mandats | API Key |
| POST | `/api/immo/mandats` | Créer un mandat | API Key |
| GET | `/api/immo/mandats/{id}` | Détail d'un mandat | API Key |
| POST | `/api/immo/mandats/{id}/compromis` | Créer compromis | API Key |
| GET | `/api/immo/compromis` | Liste des compromis | API Key |
| GET | `/api/immo/ventes/stats` | Stats (délai moyen, prix moyen) | API Key |

### 5.4 Paiement Djamo

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/immo/djamo/payment` | Créer demande de paiement | API Key + Djamo |
| GET | `/api/immo/djamo/transactions` | Liste transactions | API Key |
| POST | `/api/immo/djamo/webhook` | Notification de paiement | Signature Djamo |

### 5.5 Format des réponses

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERR_NOT_FOUND",
    "message": "Le bail demandé n'existe pas"
  }
}
```

---

## 6. Sauvegarde et restauration

### 6.1 Stratégie de sauvegarde recommandée

| Cible | Fréquence | Méthode | Rétention |
|-------|-----------|---------|-----------|
| Base de données PostgreSQL | Quotidienne, 02h00 | `pg_dump` | 30 jours |
| Documents Dolibarr | Hebdomadaire, dimanche 03h00 | `rsync` | 12 semaines |
| Configuration modules | Après chaque modification | `git push` | Historique Git |

### 6.2 Sauvegarde de la base de données

#### A. Sauvegarde manuelle

```bash
# Dump complet compressé
docker exec immo-postgres pg_dump -U dolibarr -d dolibarr -F c -f /tmp/dolibarr_$(date +%Y%m%d_%H%M%S).dump

# Copier hors du conteneur
docker cp immo-postgres:/tmp/dolibarr_20260501_020000.dump /backups/

# Nettoyer le conteneur
docker exec immo-postgres rm /tmp/dolibarr_*.dump
```

#### B. Sauvegarde planifiée (cron)

Créer un script `/opt/immobilier-ci/backup.sh` :

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backups/dolibarr"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Créer le répertoire
mkdir -p "$BACKUP_DIR"

# Sauvegarde PostgreSQL
docker exec immo-postgres pg_dump -U dolibarr -d dolibarr \
  -F c -f "/tmp/dolibarr_$DATE.dump"
docker cp "immo-postgres:/tmp/dolibarr_$DATE.dump" "$BACKUP_DIR/"
docker exec immo-postgres rm "/tmp/dolibarr_$DATE.dump"

# Compression gzip
gzip "$BACKUP_DIR/dolibarr_$DATE.dump"

# Nettoyage des vieux backups (> 30 jours)
find "$BACKUP_DIR" -name "dolibarr_*.dump.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "[$(date)] Backup completed: dolibarr_$DATE.dump.gz" >> "$BACKUP_DIR/backup.log"
```

Rendre exécutable et planifier :

```bash
chmod +x /opt/immobilier-ci/backup.sh
crontab -e
# Ajouter :
0 2 * * * /opt/immobilier-ci/backup.sh >> /var/log/dolibarr-backup.log 2>&1
```

### 6.3 Sauvegarde des documents Dolibarr

Les documents (PDF, photos, contrats) sont stockés dans le volume Docker `dolibarr_data` :

```bash
# Sauvegarde rsync
rsync -avz --delete /var/lib/docker/volumes/gestion_agence_immo_dolibarr_data/_data/ \
  /backups/dolibarr/documents/

# Ou via Docker
docker run --rm -v gestion_agence_immo_dolibarr_data:/data \
  -v /backups:/backup alpine tar czf /backup/documents_$(date +%Y%m%d).tar.gz -C /data .
```

### 6.4 Restauration de la base de données

#### A. Restauration complète (après incident majeur)

```bash
# 1. Arrêter Dolibarr
docker-compose stop dolibarr

# 2. Supprimer et recréer la base
docker exec immo-postgres psql -U dolibarr -c "DROP DATABASE dolibarr;"
docker exec immo-postgres psql -U dolibarr -c "CREATE DATABASE dolibarr OWNER dolibarr;"

# 3. Restaurer le dump
gunzip -c /backups/dolibarr_20260501_020000.dump.gz | \
  docker exec -i immo-postgres pg_restore -U dolibarr -d dolibarr -F c

# 4. Redémarrer Dolibarr
docker-compose start dolibarr
```

#### B. Restauration d'une table spécifique

```bash
# Extraire une seule table du dump
docker exec -i immo-postgres pg_restore -U dolibarr -d dolibarr \
  -F c -t llx_immo_bail /backups/dolibarr_20260501_020000.dump
```

### 6.5 Test de restauration

**Impératif** : tester la restauration mensuellement sur un environnement isolé.

```bash
# Créer un conteneur PostgreSQL de test
docker run -d --name postgres-test -e POSTGRES_PASSWORD=test postgres:15

# Restaurer le dernier backup
docker exec -i postgres-test psql -U postgres -c "CREATE DATABASE test_restore;"
gunzip -c /backups/dolibarr_$(date +%Y%m%d)_020000.dump.gz | \
  docker exec -i postgres-test pg_restore -U postgres -d test_restore -F c

# Vérifier l'intégrité
docker exec postgres-test psql -U postgres -d test_restore -c "SELECT COUNT(*) FROM llx_immo_bien;"

# Nettoyer
docker stop postgres-test && docker rm postgres-test
```

### 6.6 Snapshot Docker (méthode rapide)

Pour un rollback immédiat (avant mise à jour critique) :

```bash
# Sauvegarder les volumes
docker run --rm -v gestion_agence_immo_postgres_data:/data \
  -v /backups:/backup alpine tar czf /backup/postgres_snapshot_$(date +%Y%m%d).tar.gz -C /data .

# Restaurer
docker run --rm -v gestion_agence_immo_postgres_data:/data \
  -v /backups:/backup alpine sh -c "cd /data && tar xzf /backup/postgres_snapshot_20260501.tar.gz"
```

---

## 7. Migration

### 7.1 Mise à jour Dolibarr (ex: 23.x → 24.x)

#### A. Avant la migration

1. **Sauvegarde complète** (voir §6.2 et §6.3)
2. **Vérifier la compatibilité** des modules :
   ```bash
   # Vérifier que les classes CommonObject n'ont pas changé
   docker exec immo-dolibarr php -l /var/www/html/custom/immocore/class/*.php
   ```
3. **Créer un environnement de test** avec la nouvelle version

#### B. Procédure de migration

```bash
# 1. Arrêter les services
docker-compose down

# 2. Sauvegarder les volumes
docker volume ls | grep immo
docker run --rm -v gestion_agence_immo_postgres_data:/data \
  -v /backups:/backup alpine tar czf /backup/pre_migration_postgres.tar.gz -C /data .

# 3. Modifier la version dans docker-compose.yml
# image: dolibarr/dolibarr:24.0.0

# 4. Redémarrer avec la nouvelle image
docker-compose up -d

# 5. Exécuter les scripts de migration Dolibarr
# http://localhost:8080/install/
# Sélectionner "Mise à jour" et suivre les étapes

# 6. Vérifier les modules
docker exec immo-dolibarr ls -la /var/www/html/custom/
```

#### C. Scripts SQL de migration des modules

Si des changements de schéma SQL sont nécessaires, créer un fichier `sql/migration_1.x_to_1.y.sql` :

```sql
-- Migration immolocatif 1.0 → 1.1
-- Ajouter le champ date_prochaine_indexation

ALTER TABLE llx_immo_bail
ADD COLUMN IF NOT EXISTS date_prochaine_indexation DATE;

UPDATE llx_immo_bail
SET date_prochaine_indexation = date_debut + INTERVAL '1 year'
WHERE statut = 'actif';

-- Journaliser la migration
INSERT INTO llx_immo_migrations (version, applied_at, description)
VALUES ('1.1', NOW(), 'Ajout date_prochaine_indexation');
```

> **Règle** : Chaque module dispose d'une table `llx_immo_migrations` pour tracer les migrations appliquées.

#### D. Rollback en cas d'échec

```bash
# 1. Arrêter les services
docker-compose down

# 2. Restaurer les volumes pré-migration
docker run --rm -v gestion_agence_immo_postgres_data:/data \
  -v /backups:/backup alpine sh -c "cd /data && rm -rf * && tar xzf /backup/pre_migration_postgres.tar.gz"

# 3. Revenir à l'ancienne image
docker-compose up -d
```

### 7.2 Migration de base de données (PostgreSQL)

#### A. Mise à jour PostgreSQL (ex: 15 → 16)

```bash
# 1. Sauvegarde complète
docker exec immo-postgres pg_dumpall -U dolibarr > /backups/full_dump.sql

# 2. Arrêter les services
docker-compose down

# 3. Modifier docker-compose.yml : image: postgres:16

# 4. Supprimer l'ancien volume (ATTENTION : données perdues)
docker volume rm gestion_agence_immo_postgres_data

# 5. Redémarrer
docker-compose up -d db

# 6. Restaurer
docker exec -i immo-postgres psql -U dolibarr < /backups/full_dump.sql

# 7. Redémarrer Dolibarr
docker-compose up -d dolibarr
```

#### B. Export vers un autre serveur

```bash
# Dump complet
docker exec immo-postgres pg_dumpall -U dolibarr > /backups/full_export.sql

# Transfert scp
scp /backups/full_export.sql admin@newserver:/backups/

# Import sur le nouveau serveur
psql -U dolibarr -f /backups/full_export.sql
```

---

## 8. Troubleshooting

### 8.1 Tableau des problèmes courants

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| **Page blanche après activation d'un module** | Erreur PHP dans le fichier du module | Vérifier `docker logs immo-dolibarr`, corriger la syntaxe |
| **Les tables SQL n'existent pas** | Scripts SQL non exécutés | Exécuter les fichiers `.sql` dans psql/pgAdmin |
| **TLPPU calculé à 0** | Taux non configuré (ni sur le bien, ni par défaut) | Configurer `IMMO_TAUX_TLPPU_DEFAUT` ou le taux sur le bien |
| **Erreur "Class not found"** | Fichier de classe manquant ou mal nommé | Vérifier la présence dans `class/`, vérifier le nom du fichier |
| **Tests PHPUnit rouges** | Classe mock manquante ou propriété typée incompatible | Vérifier `bootstrap.php`, supprimer les types PHP 8 (`string`, `int`) sur les propriétés héritées de `CommonObject` |
| **Push GitHub échoue** | Condition de course ou clé SSH absente | Vérifier `git remote -v`, vérifier la clé SSH `ssh -T git@github.com` |
| **Docker Compose ne démarre pas** | Erreur de syntaxe YAML ou port occupé | Vérifier `docker-compose.yml` avec un validateur, libérer les ports 8080/5432/8081 |
| **Dolibarr affiche " erreur technique"** | `$dolibarr_main_prod=1` empêche le debug | Modifier `conf.php` temporairement en mode dev |
| **Quittances impayées non alertées** | Cron Dolibarr non configuré | Activer le cron Dolibarr ou lancer `scripts/cron.php` manuellement |
| **Paiement Djamo non enregistré** | Webhook mal configuré | Vérifier l'URL du webhook, la signature, les logs Dolibarr |
| **Erreur SQL "relation n'existe pas"** | Table manquante ou préfixe incorrect | Vérifier l'exécution des scripts SQL, vérifier `MAIN_DB_PREFIX` |
| **Erreur "datetime does not exist"** | Fichier SQL avec type MySQL | Remplacer `datetime` par `timestamp` dans tous les fichiers `.sql` |
| **Connexion PostgreSQL refusée** | Mauvais host/port ou conteneur arrêté | Vérifier `DOLI_DB_HOST=db` (nom du service Docker), vérifier que le conteneur `immo-postgres` est actif |

### 8.2 Diagnostic avancé

#### A. Logs Dolibarr en temps réel

```bash
docker logs -f immo-dolibarr
docker logs -f immo-dolibarr 2>&1 | grep -i error
```

#### B. Logs PostgreSQL

```bash
docker exec immo-postgres cat /var/lib/postgresql/data/log/postgresql-$(date +%Y-%m-%d).log
# Ou
docker exec immo-postgres psql -U dolibarr -c "SELECT * FROM pg_stat_activity;"
```

#### C. Vérifier l'intégrité des modules

```bash
# Vérifier la syntaxe PHP de tous les fichiers
for f in $(find /var/www/html/custom/imm* -name "*.php"); do
    php -l "$f" 2>&1 | grep -v "No syntax errors"
done

# Vérifier que les fichiers SQL sont valides
for f in $(find /var/www/html/custom/imm* -name "*.sql"); do
    docker exec -i immo-postgres psql -U dolibarr -f "$f" 2>&1 | grep ERROR
done
```

#### D. Réinitialiser un module

```bash
# Désactiver et réactiver un module
# Dans Dolibarr : Configuration > Modules > Désactiver > Réactiver

# Ou via SQL
docker exec immo-postgres psql -U dolibarr -c "UPDATE llx_const SET value = 0 WHERE name = 'MAIN_MODULE_IMMOCORE';"
```

### 8.3 Problèmes spécifiques de tests

| Erreur PHPUnit | Cause | Solution |
|----------------|-------|----------|
| `Failed opening required 'DolibarrModules.class.php'` | Stub manquant | Créer `/home/hdl/src/core/modules/DolibarrModules.class.php` factice |
| `Cannot declare class X, because the name is already in use` | Conflit de nom de classe (insensible à la casse) | Renommer le fichier test ou supprimer le doublon |
| `Type of X::$ref must not be defined` | Propriété typée incompatible avec `CommonObject` | Supprimer le type `string` / `int` sur les propriétés héritées |
| `Class X cannot be found in file` | Nom de fichier différent du nom de classe | Renommer le fichier pour correspondre exactement à `class X` |

---

## 9. Monitoring

### 9.1 Health checks Docker

#### A. Script de vérification de santé

Créer `/opt/immobilier-ci/healthcheck.sh` :

```bash
#!/bin/bash
# Health check des services immobiliers

EXIT_CODE=0

echo "=== $(date) ==="

# Vérifier PostgreSQL
if docker exec immo-postgres pg_isready -U dolibarr > /dev/null 2>&1; then
    echo "✅ PostgreSQL : OK"
else
    echo "❌ PostgreSQL : DOWN"
    EXIT_CODE=1
fi

# Vérifier Dolibarr (HTTP 200)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Dolibarr : OK (HTTP $HTTP_CODE)"
else
    echo "❌ Dolibarr : DOWN (HTTP $HTTP_CODE)"
    EXIT_CODE=1
fi

# Vérifier l'espace disque
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    echo "✅ Disque : ${DISK_USAGE}% utilisé"
else
    echo "⚠️ Disque : ${DISK_USAGE}% utilisé (alerte)"
    EXIT_CODE=1
fi

# Vérifier la mémoire
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEMORY_USAGE" -lt 90 ]; then
    echo "✅ Mémoire : ${MEMORY_USAGE}% utilisée"
else
    echo "⚠️ Mémoire : ${MEMORY_USAGE}% utilisée (alerte)"
    EXIT_CODE=1
fi

# Vérifier les tests PHPUnit
if cd /opt/immobilier-ci/dolibarr-agence-immocore/test/phpunit && \
   /opt/immobilier-ci/vendor/bin/phpunit --bootstrap bootstrap.php . > /dev/null 2>&1; then
    echo "✅ Tests immocore : PASS"
else
    echo "❌ Tests immocore : FAIL"
    EXIT_CODE=1
fi

exit $EXIT_CODE
```

#### B. Intégration au cron

```bash
chmod +x /opt/immobilier-ci/healthcheck.sh
crontab -e
# Ajouter toutes les 5 minutes :
*/5 * * * * /opt/immobilier-ci/healthcheck.sh >> /var/log/immo-health.log 2>&1
```

### 9.2 Alertes et notifications

#### A. Alertes par email (via script)

```bash
# Ajouter à healthcheck.sh :
if [ $EXIT_CODE -ne 0 ]; then
    echo "Alerte immobilier : service dégradé" | \
    mail -s "[ALERTE] Immobilier CI - $(date)" admin@agence.ci
fi
```

#### B. Alertes Slack/Discord (webhook)

```bash
# Notification Slack
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"❌ Alerte Immobilier : PostgreSQL DOWN sur $(hostname)\"}" \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 9.3 Métriques Docker

#### A. Utilisation des ressources

```bash
# Statistiques des conteneurs en temps réel
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Historique CPU/mémoire
docker stats --no-stream --format "{{.Name}}: CPU={{.CPUPerc}} MEM={{.MemPerc}}"
```

#### B. Logs centralisés

```bash
# Agréger tous les logs
docker-compose logs -f --tail=100

# Exporter les logs pour analyse
docker-compose logs > /var/log/immo-$(date +%Y%m%d).log
```

### 9.4 Monitoring PostgreSQL

#### A. Requêtes lentes

```bash
docker exec immo-postgres psql -U dolibarr -c "
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"
```

#### B. Connexions actives

```bash
docker exec immo-postgres psql -U dolibarr -c "
SELECT pid, usename, application_name, client_addr, state, query_start
FROM pg_stat_activity
WHERE state = 'active';
"
```

#### C. Taille des tables

```bash
docker exec immo-postgres psql -U dolibarr -c "
SELECT schemaname, relname, pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname))
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC;
"
```

### 9.5 Monitoring GitHub Actions CI/CD

#### A. Vérifier l'état des workflows

```bash
# Vérifier le statut du dernier workflow
cd /opt/immobilier-ci/dolibarr-agence-immocore
gh run list --limit 5

# Voir les logs d'un run spécifique
gh run view <run-id> --log
```

#### B. Badge de statut dans README

Ajouter dans chaque `README.md` :

```markdown
![Tests](https://github.com/laurenthdl/dolibarr-agence-immocore/actions/workflows/tests.yml/badge.svg)
```

#### C. Notification d'échec CI

Configurer dans `.github/workflows/tests.yml` :

```yaml
- name: Notify on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {"text": "❌ Tests échoués sur ${{ github.repository }}"}
```

### 9.6 Tableau de bord de monitoring (optionnel)

Pour un monitoring avancé, déployer **Prometheus + Grafana** :

```yaml
# À ajouter dans docker-compose.yml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

Métriques à collecter :
- Taux d'occupation des biens (depuis `llx_immo_bien`)
- Taux d'encaissement mensuel (depuis `llx_immo_quittance`)
- Nombre de transactions Djamo par jour (depuis `llx_immo_paiement_mobile`)
- Délai moyen de vente (depuis `llx_immo_mandat_vente`)

---

## 10. Support et ressources

### 10.1 Ressources officielles

| Ressource | URL | Usage |
|-----------|-----|-------|
| Dépôts GitHub | `github.com/laurenthdl/dolibarr-agence-*` | Code source, issues, releases |
| Documentation Dolibarr | `https://wiki.dolibarr.org` | ERP natif, hooks, API |
| Documentation PostgreSQL | `https://www.postgresql.org/docs/15/` | SQL, administration, optimisation |
| Docker Hub Dolibarr | `https://hub.docker.com/r/dolibarr/dolibarr` | Images officielles |

### 10.2 Contact support

| Type de demande | Canal | Délai de réponse |
|-----------------|-------|------------------|
| Bug technique | GitHub Issues | 48h ouvrées |
| Demande de fonctionnalité | GitHub Discussions | 72h ouvrées |
| Urgence production | Email direct | 4h ouvrées |
| Question utilisateur | Documentation | Immédiat (self-service) |

### 10.3 Glossaire technique

| Terme | Définition |
|-------|------------|
| **TLPPU** | Taxe Locale sur la Propriété et la Publicité — taxe communale perçue sur les loyers |
| **Tantième** | Part proportionnelle dans une copropriété (généralement sur 1000) |
| **Webhook** | Notification HTTP automatique envoyée par un service tiers (ex: Djamo) |
| **Quittance** | Document attestant du paiement du loyer pour une période donnée |
| **Compromis** | Promesse de vente signée par le vendeur et l'acheteur |
| **Mandat** | Contrat confiant la vente d'un bien à une agence |
| **Bail** | Contrat de location entre propriétaire et locataire |
| **Hook Dolibarr** | Point d'extension permettant d'intercepter des événements sans modifier le core |

---

*Référence Technique — Gestion Agence Immobilière Côte d'Ivoire | v1.0 | Mai 2026*
