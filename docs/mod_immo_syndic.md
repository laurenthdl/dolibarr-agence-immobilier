# Module `mod_immo_syndic` — Syndic de Copropriété

## Objectif

Gérer les aspects du syndic de copropriété : immeubles, lots, tantièmes, charges communes, appels de fonds, et assemblées générales. Prévu pour une future intégration avec le cadastre DGFLTI.

## Fonctionnalités

### 1. Immeubles et lots

Un **Immeuble** est un type de bien spécifique. Il contient des **Lots** (appartements, parkings, caves, locaux commerciaux).

| Élément | Description |
|---------|-------------|
| Immeuble | Fiche bien de type "Immeuble", adresse, nombre de lots |
| Lot | Numéro, type, surface, tantième, propriétaire |
| Tantième | Parts de charges (exprimées en millièmes) |

### 2. Charges communes

| Type | Description | Répartition |
|------|-------------|-------------|
| Charges générales | Ascenseur, éclairage, eau commune | Selon tantièmes |
| Chauffage collectif | Si applicable | Selon tantièmes ou compteurs |
| Entretien espaces verts | Jardin, cour | Selon tantièmes |
| Gardiennage | Concierge/gardien | Selon tantièmes |
| Assurance immeuble | Assurance dommages-ouvrage | Selon tantièmes |

### 3. Appels de fonds

| Élément | Description |
|---------|-------------|
| Période | Mensuel, trimestriel, annuel |
| Budget prévisionnel | Charges estimées pour la période |
| Appel | Montant à payer par lot (budget × tantième / 1000) |
| Paiement | Suivi des paiements par copropriétaire |
| Solde | Relance si impayé |

### 4. Assemblées générales

| Élément | Description |
|---------|-------------|
| Date | Date de l'AG |
| Ordre du jour | Points à traiter |
| Procès-verbal | Compte-rendu |
| Votes | Résolutions votées |
| Quorum | Nombre de tantièmes présents/représentés |

## Schéma de base de données

### `llx_immo_syndic_lot`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence lot (LOT-XXXX) |
| fk_bien_immeuble | INTEGER | Référence immeuble |
| numero | VARCHAR(32) | Numéro de lot |
| type_lot | VARCHAR(32) | appartement, parking, cave, local |
| surface | DECIMAL(24,8) | Surface en m² |
| tantieme | INTEGER | Parts en millièmes |
| fk_proprietaire | INTEGER | Propriétaire |
| fk_locataire | INTEGER | Locataire (si loué) |
| statut | VARCHAR(32) | occupe, vide, en_travaux |
| fk_user_creat | INTEGER | Auteur |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

### `llx_immo_syndic_charge`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_immeuble | INTEGER | Référence immeuble |
| label | VARCHAR(255) | Libellé charge |
| type_charge | VARCHAR(32) | generale, chauffage, jardin, gardiennage, assurance |
| budget_annuel | DECIMAL(24,8) | Budget prévisionnel annuel |
| periode_appel | VARCHAR(32) | mensuel, trimestriel, annuel |

### `llx_immo_syndic_appel`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence appel (APP-XXXX) |
| fk_immeuble | INTEGER | Référence immeuble |
| periode_annee | INTEGER | Année |
| periode_mois | INTEGER | Mois (si mensuel) |
| montant_total | DECIMAL(24,8) | Montant total appelé |
| date_emission | DATE | Date émission |
| date_echeance | DATE | Date échéance |
| statut | VARCHAR(32) | brouillon, emis, partiel, solde |

### `llx_immo_syndic_appel_lot`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_appel | INTEGER | Référence appel |
| fk_lot | INTEGER | Référence lot |
| montant_du | DECIMAL(24,8) | Montant dû (selon tantième) |
| montant_paye | DECIMAL(24,8) | Montant payé |
| solde | DECIMAL(24,8) | Solde |

### `llx_immo_syndic_ag`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_immeuble | INTEGER | Référence immeuble |
| date_ag | DATE | Date AG |
| ordre_jour | TEXT | Ordre du jour |
| pv | TEXT | Procès-verbal |
| quorum_tantiemes | INTEGER | Tantièmes présents/représentés |
| statut | VARCHAR(32) | planifiee, tenue, annulee |

## Interface utilisateur

### Fiche immeuble (vue syndic)
- Onglets : Informations, Lots, Charges, Appels de fonds, Assemblées
- Plan de l'immeuble (liste des lots avec statut couleur)
- Total des tantièmes : doit faire 1000

### Appel de fonds
- Génération massive par période
- Répartition automatique selon tantièmes
- Quittance par lot

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/syndic/immeubles` | Liste immeubles en syndic |
| GET | `/api/immo/syndic/lots` | Liste lots |
| POST | `/api/immo/syndic/appels` | Créer appel de fonds |
| GET | `/api/immo/syndic/appels/{id}` | Détail appel |
| POST | `/api/immo/syndic/appels/{id}/lots` | Répartir par lots |
| GET | `/api/immo/syndic/ags` | Liste AG |

## Dépendances

- **Requis** : `mod_immo_core`, `mod_immo_bien`, `mod_immo_client`
- **Utilise** : `mod_societe`

## Configuration

Numéro de module : **700006**
Classe : `modImmosyndic`

## Notes de développement

- La somme des tantièmes d'un immeuble doit toujours être contrôlée (= 1000)
- L'appel de fonds peut être lié au module Comptabilité Dolibarr
- Prévoir un modèle ODT pour la convocation AG et le PV
- La gestion des lots peut être liée au module `immo_locatif` si un lot est loué
