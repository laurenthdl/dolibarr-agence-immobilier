# Guide Administrateur — Gestion Agence Immobilière Côte d'Ivoire

> Version 1.0 | Dolibarr 23.x | Modules `700000` — `700009`
> **Public cible** : Administrateurs système, Responsables informatiques, Intégrateurs Dolibarr

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Prérequis système](#2-prérequis-système)
3. [Installation](#3-installation)
4. [Configuration initiale](#4-configuration-initiale)
5. [Catalogue de référence](#5-catalogue-de-référence)
6. [Gestion des droits utilisateurs](#6-gestion-des-droits-utilisateurs)
7. [Maintenance et mise à jour](#7-maintenance-et-mise-à-jour)

---

## 1. Vue d'ensemble du projet

### 1.1 Objectif

Cette suite de modules Dolibarr transforme l'ERP en un **vertical immobilier complet** adapté aux agences de Côte d'Ivoire. Elle couvre l'ensemble du cycle de vie d'un bien immobilier :

- **Gestion locative** : baux, quittances, échéancier, TLPPU automatique
- **Transactions de vente** : mandats, compromis, commissions
- **Suivi de rénovation** : budget, avancement, changement d'état
- **Syndic de copropriété** : charges, appels de fonds, répartition par tantième
- **Étude de marché** : saisie de comparables, prix au m²
- **Paiement mobile** : intégration Djamo pour encaissement des loyers
- **Rapports décisionnels** : tableaux de bord, KPIs, exports

### 1.2 Architecture modulaire

Les 10 modules fonctionnent de manière indépendante mais interconnectée :

```
┌─────────────────────────────────────────────────────────────────┐
│                         mod_immo_core (700000)                  │
│              Configuration, activation modules, droits           │
└─────────────────────────────────────────────────────────────────┘
                                │
    ┌───────────┬───────────┬───┴───┬───────────┬───────────┐
    ▼           ▼           ▼       ▼           ▼           ▼
 immobien   immoclient  immolocatif immovente [Extensions]
(700001)    (700002)    (700003)  (700004)   immoreno, immosyndic,
                                          immomarche, immodjamo,
                                          immorapports (700005-700009)
```

Chaque module est **activable/désactivable** individuellement depuis le panneau de configuration `Immobilier > Configuration`.

### 1.3 Stack technique

| Couche | Technologie | Version |
|--------|-------------|---------|
| ERP | Dolibarr | 23.x |
| Langage | PHP | 8.1+ |
| Base de données | PostgreSQL | 15 |
| Conteneurisation | Docker + Docker Compose | 24+ |
| Serveur web | Apache/Nginx | Avec mod_rewrite |
| Paiement | API REST Djamo | Sandbox / Production |
| Tests | PHPUnit | 11 |

---

## 2. Prérequis système

### 2.1 Serveur recommandé (Docker)

| Ressource | Minimum | Recommandé |
|-----------|---------|------------|
| CPU | 2 cœurs | 4 cœurs |
| RAM | 4 Go | 8 Go |
| Disque | 20 Go SSD | 50 Go SSD |
| Réseau | 10 Mbps | 100 Mbps |

### 2.2 Logiciels requis

| Composant | Version requise | Vérification |
|-----------|-----------------|--------------|
| Docker Engine | 24.0+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| Git | 2.30+ | `git --version` |

### 2.3 Accès nécessaires

| Ressource | Usage |
|-----------|-------|
| Port 8080 (HTTP) | Interface Dolibarr |
| Port 5432 (PostgreSQL) | Base de données (interne Docker) |
| Port 8081 (HTTP) | pgAdmin (interface DB, optionnel) |
| Accès Internet | Clonage des repositories, API Djamo |

---

## 3. Installation

### 3.1 Installation via Docker (recommandée)

Cette méthode est la plus rapide et garantit un environnement identique entre développement et production.

#### Étape 1 : Cloner les repositories

Chaque module dispose de son propre repository GitHub. Créez un répertoire parent et clonez les 10 modules :

```bash
mkdir -p /opt/immobilier-ci
cd /opt/immobilier-ci

# Cloner chaque module
git clone https://github.com/laurenthdl/dolibarr-agence-immocore.git
git clone https://github.com/laurenthdl/dolibarr-agence-immobien.git
git clone https://github.com/laurenthdl/dolibarr-agence-immoclient.git
git clone https://github.com/laurenthdl/dolibarr-agence-immolocatif.git
git clone https://github.com/laurenthdl/dolibarr-agence-immovente.git
git clone https://github.com/laurenthdl/dolibarr-agence-immoreno.git
git clone https://github.com/laurenthdl/dolibarr-agence-immosyndic.git
git clone https://github.com/laurenthdl/dolibarr-agence-immomarche.git
git clone https://github.com/laurenthdl/dolibarr-agence-immodjamo.git
git clone https://github.com/laurenthdl/dolibarr-agence-immorapports.git
```

#### Étape 2 : Créer le fichier docker-compose.yml

Créez à la racine du répertoire parent :

```yaml
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
    ports:
      - "5432:5432"
    networks:
      - immo-network

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
      - db
    networks:
      - immo-network

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
```

#### Étape 3 : Lancer l'infrastructure

```bash
cd /opt/immobilier-ci
docker-compose up -d
```

Vérifier que les conteneurs sont actifs :

```bash
docker-compose ps
```

#### Étape 4 : Finaliser l'installation Dolibarr

1. Ouvrir un navigateur : `http://localhost:8080/install/`
2. Sélectionner la langue : **Français**
3. Accepter la licence GPL
4. Tester la connexion à la base de données :
   - **Type** : PostgreSQL
   - **Serveur** : `db`
   - **Port** : `5432`
   - **Base** : `dolibarr`
   - **Utilisateur** : `dolibarr`
   - **Mot de passe** : `dolibarr`
5. Créer le compte administrateur
6. Finaliser l'installation

#### Étape 5 : Activer les modules

1. Se connecter à Dolibarr (`http://localhost:8080`)
2. Menu `Configuration > Modules/Applications`
3. Activer dans cet ordre :
   1. **immocore** (700000) — doit être activé en premier
   2. **immobien** (700001)
   3. **immoclient** (700002)
   4. **immolocatif** (700003)
   5. Les autres modules selon les besoins
4. Vérifier que le menu **Immobilier** apparaît dans la barre supérieure

### 3.2 Installation manuelle (serveur dédié)

Si vous ne pouvez pas utiliser Docker, suivez ces étapes sur votre serveur Dolibarr existant.

#### Étape 1 : Copier les modules

Copier chaque dossier de module dans `htdocs/custom/` :

```bash
cp -r dolibarr-agence-immocore /var/www/dolibarr/htdocs/custom/immocore
cp -r dolibarr-agence-immobien /var/www/dolibarr/htdocs/custom/immobien
# ... répéter pour les 10 modules
```

#### Étape 2 : Créer les tables SQL

Se connecter à PostgreSQL et exécuter les scripts SQL de chaque module :

```bash
psql -U dolibarr -d dolibarr -f /var/www/dolibarr/htdocs/custom/immobien/sql/llx_immo_bien.sql
psql -U dolibarr -d dolibarr -f /var/www/dolibarr/htdocs/custom/immolocatif/sql/llx_immo_bail.sql
# ... répéter pour tous les fichiers .sql
```

> **Important** : Le module **immocore** doit être activé en premier. Les autres modules dépendent des catalogues et de la configuration qu'il crée.

#### Étape 3 : Activer les modules

Dans Dolibarr : `Configuration > Modules/Applications > Immobilier`

#### Étape 4 : Vérifier les permissions

S'assurer que le serveur web a les droits de lecture sur les dossiers des modules :

```bash
chown -R www-data:www-data /var/www/dolibarr/htdocs/custom/imm*
chmod -R 755 /var/www/dolibarr/htdocs/custom/imm*
```

---

## 4. Configuration initiale

### 4.1 Accéder au panneau de configuration

Menu `Immobilier > Configuration` (module immocore — 700000).

### 4.2 Paramètres globaux

| Paramètre | Valeur par défaut | Description | Quand modifier |
|-----------|-------------------|-------------|----------------|
| `IMMO_REF_PREFIX_BIEN` | `IMMO` | Préfixe des références bien | Rarement |
| `IMMO_REF_PREFIX_BAIL` | `BAIL` | Préfixe des références bail | Rarement |
| `IMMO_REF_PREFIX_QUITTANCE` | `QUIT` | Préfixe des références quittance | Rarement |
| `IMMO_TAUX_TLPPU_DEFAUT` | `15.00` | Taux TLPPU par défaut (%) | Selon la commune principale |
| `IMMO_COMMUNE_DEFAUT` | `Abidjan` | Commune par défaut | Selon le siège de l'agence |
| `IMMO_DEVISE` | `XOF` | Devise principale | Ne pas modifier (FCFA) |

### 4.3 Activation des modules

Chaque module peut être activé ou désactivé indépendamment :

| Paramètre | Défaut | Module concerné |
|-----------|--------|-----------------|
| `IMMO_ACTIVATE_CORE` | 1 (activé) | Core (toujours actif) |
| `IMMO_ACTIVATE_BIEN` | 1 (activé) | Biens |
| `IMMO_ACTIVATE_CLIENT` | 1 (activé) | Clients |
| `IMMO_ACTIVATE_LOCATIF` | 1 (activé) | Gestion locative |
| `IMMO_ACTIVATE_VENTE` | 0 (désactivé) | Transactions de vente |
| `IMMO_ACTIVATE_RENO` | 0 (désactivé) | Rénovation |
| `IMMO_ACTIVATE_SYNDIC` | 0 (désactivé) | Syndic de copropriété |
| `IMMO_ACTIVATE_MARCHE` | 0 (désactivé) | Étude de marché |
| `IMMO_ACTIVATE_DJAMO` | 0 (désactivé) | Paiement mobile Djamo |
| `IMMO_ACTIVATE_RAPPORTS` | 0 (désactivé) | Rapports et tableaux de bord |

> **Règle** : Activez les modules selon les besoins réels de l'agence. Un module désactivé n'apparaît pas dans les menus et ne consomme pas de ressources.

### 4.4 Configuration Djamo (si module activé)

Si vous activez le module **immodjamo** (700008), configurer les identifiants API :

1. Menu `Immobilier > Configuration > Paiements`
2. Renseigner :
   - **DJAMO_CLIENT_ID** : identifiant fourni par Djamo
   - **DJAMO_CLIENT_SECRET** : secret fourni par Djamo
   - **DJAMO_ENV** : `sandbox` pour les tests, `production` pour le réel
3. Tester la connexion avec le bouton **Vérifier**

> Obtenir les identifiants : [Centre Développeur Djamo](https://developer.djamo.com)

---

## 5. Catalogue de référence

L'administrateur doit peupler les catalogues suivants avant que les agents puissent utiliser le système.

### 5.1 Accéder aux catalogues

Menu `Immobilier > Configuration > Catalogues`

### 5.2 Types de bien

| Code | Libellé | À personnaliser |
|------|---------|-----------------|
| `MAISON` | Maison individuelle | Non |
| `APPART` | Appartement | Non |
| `BUREAU` | Bureau | Non |
| `BOUTIQUE` | Boutique / Commerce | Non |
| `ENTREPOT` | Entrepôt / Hangar | Oui selon le marché |
| `TERRAIN` | Terrain nu | Non |
| `IMMEUBLE` | Immeuble complet | Non |

### 5.3 États de bien

| Code | Libellé | Couleur | Signification |
|------|---------|---------|---------------|
| `A_ACQUERIR` | À acquérir | Gris | L'agence ne gère pas encore le bien |
| `DISPONIBLE` | Disponible | Vert clair | Prêt à être mis sur le marché |
| `A_LOUER` | À louer | Bleu | Actuellement proposé à la location |
| `LOUE` | Loué | Vert foncé | Un bail actif est en cours |
| `A_VENDRE` | À vendre | Orange | Actuellement proposé à la vente |
| `VENDU` | Vendu | Rouge | Transaction finalisée |
| `RENOVATION` | En rénovation | Jaune | Travaux en cours |
| `ARCHIVE` | Archivé | Noir | Plus géré par l'agence |

### 5.4 Types de bail

| Code | Libellé | Durée par défaut |
|------|---------|------------------|
| `RES_VIDE` | Résidentiel vide | 12 mois |
| `RES_MEUBLE` | Résidentiel meublé | 6 mois |
| `COMMERCIAL` | Commercial | 36 mois (3-6-9) |
| `PROFESSIONNEL` | Professionnel | 36 mois |
| `SAISONNIER` | Saisonnier | 3 mois |

### 5.5 Types de client

| Code | Libellé | Usage |
|------|---------|-------|
| `PROPRIETAIRE` | Propriétaire | Confie un bien à l'agence |
| `LOCATAIRE` | Locataire | Occupe un bien en location |
| `ACHETEUR` | Acheteur | Intéressé par un achat |
| `PROSPECT` | Prospect | Contact potentiel |
| `BAILLEUR` | Bailleur | Investisseur avec plusieurs biens |
| `SYNDIC` | Syndic | Gère une copropriété |

### 5.6 Modes de paiement

| Code | Libellé | Configuration requise |
|------|---------|----------------------|
| `ESPECES` | Espèces | Aucune |
| `VIREMENT` | Virement bancaire | Aucune |
| `CHEQUE` | Chèque | Aucune |
| `DJAMO` | Djamo | Identifiants API configurés |
| `OM` | Orange Money | Identifiants API (futur) |
| `MTN` | MTN Mobile Money | Identifiants API (futur) |

---

## 6. Gestion des droits utilisateurs

### 6.1 Profils prédéfinis

| Profil | Permissions | Usage |
|--------|-------------|-------|
| **Administrateur** | `immo_admin` + toutes les permissions | Configuration, tous les modules |
| **Directeur d'agence** | `immo_read`, `immo_write`, `immo_delete`, `immo_rapport_voir` | Supervision globale, rapports |
| **Agent commercial** | `immo_read`, `immo_write`, `immo_mandat_creer` | Visites, mandats, ventes |
| **Gestionnaire locatif** | `immo_read`, `immo_write`, `immo_quittance_generate` | Baux, quittances, échéancier |
| **Comptable** | `immo_read`, `immo_rapport_voir` | Suivi financier, exports |
| **Assistant** | `immo_read` | Consultation uniquement |

### 6.2 Créer un profil personnalisé

1. Menu `Configuration > Utilisateurs > Groupes`
2. Créer un groupe (ex: "Agents Cocody")
3. Attribuer les permissions immobilières :
   - **immo_read** : lecture des données (obligatoire pour tous)
   - **immo_write** : création/modification
   - **immo_delete** : suppression/archivage
   - **immo_admin** : configuration (réservé aux admins)
4. Assigner les utilisateurs au groupe

### 6.3 Matrice des permissions par module

| Permission | Core | Bien | Client | Locatif | Vente | Reno | Syndic | Marché | Djamo | Rapports |
|------------|------|------|--------|---------|-------|------|--------|--------|-------|----------|
| `immo_read` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `immo_write` | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `immo_delete` | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `immo_quittance_generate` | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `immo_mandat_creer` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `immo_rapport_voir` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 7. Maintenance et mise à jour

### 7.1 Mise à jour des modules

Lorsqu'une nouvelle version d'un module est publiée :

```bash
cd /opt/immobilier-ci/dolibarr-agence-immocore
git pull origin main
# Répéter pour chaque module concerné

# Redémarrer le conteneur Dolibarr
docker-compose restart dolibarr
```

### 7.2 Vérification de l'intégrité

Après chaque mise à jour :

1. Vérifier que tous les modules sont actifs dans Dolibarr
2. Vérifier que les tables SQL sont à jour (comparer avec les scripts du dossier `sql/`)
3. Exécuter la suite de tests PHPUnit :
   ```bash
   cd /opt/immobilier-ci/dolibarr-agence-immocore/test/phpunit
   ./vendor/bin/phpunit --bootstrap bootstrap.php .
   ```

### 7.3 Sauvegarde planifiée

Configurez une sauvegarde automatique (voir [Référence Technique — Sauvegarde](Reference_Technique.md#sauvegarde-et-restauration)).

### 7.4 Logs et diagnostic

| Fichier / Commande | Usage |
|--------------------|-------|
| `docker logs immo-dolibarr` | Logs Dolibarr |
| `docker logs immo-postgres` | Logs PostgreSQL |
| `/var/www/html/documents/dolibarr.log` | Logs applicatifs Dolibarr |
| `docker exec -it immo-postgres psql -U dolibarr` | Accès SQL direct |

---

*Guide Administrateur — Gestion Agence Immobilière Côte d'Ivoire | v1.0 | Mai 2026*
