# Module `mod_immo_core` — Base Commune

## Objectif

Fournir l'architecture commune à tous les modules immobiliers : configuration globale, système d'activation des modules, gestion des droits, hooks cadastre, et tables pivot partagées.

## Fonctionnalités

### 1. Configuration globale

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| `IMMO_REF_PREFIX_BIEN` | Préfixe référence bien | `IMMO` |
| `IMMO_REF_PREFIX_BAIL` | Préfixe référence bail | `BAIL` |
| `IMMO_REF_PREFIX_QUITTANCE` | Préfixe référence quittance | `QUIT` |
| `IMMO_REF_PREFIX_VISITE` | Préfixe référence visite | `VIS` |
| `IMMO_TAUX_TLPPU_DEFAUT` | Taux TLPPU par défaut (%) | `15.00` |
| `IMMO_COMMUNE_DEFAUT` | Commune par défaut | `Abidjan` |
| `IMMO_DEVISE` | Devise principale | `XOF` |
| `IMMO_ACTIVATE_CORE` | Activation core | `1` |
| `IMMO_ACTIVATE_BIEN` | Activation module bien | `1` |
| `IMMO_ACTIVATE_CLIENT` | Activation module client | `1` |
| `IMMO_ACTIVATE_LOCATIF` | Activation module locatif | `1` |
| `IMMO_ACTIVATE_VENTE` | Activation module vente | `0` |
| `IMMO_ACTIVATE_RENO` | Activation module rénovation | `0` |
| `IMMO_ACTIVATE_SYNDIC` | Activation module syndic | `0` |
| `IMMO_ACTIVATE_MARCHE` | Activation module marché | `0` |
| `IMMO_ACTIVATE_DJAMO` | Activation module Djamo | `0` |
| `IMMO_ACTIVATE_RAPPORTS` | Activation module rapports | `0` |

### 2. Catalogue de référence

Tables de catalogue utilisées par tous les modules :

| Table | Description | Valeurs |
|-------|-------------|---------|
| `llx_immo_type_bien` | Types de biens | Maison, Appartement, Bureau, Boutique, Entrepôt, Terrain, Immeuble |
| `llx_immo_etat_bien` | États d'un bien | À acquérir, Disponible, À rénover, En rénovation, À louer, Loué, À vendre, Vendu, Archivé |
| `llx_immo_type_bail` | Types de bail | Résidentiel vide, Résidentiel meublé, Commercial, Professionnel, Saisonnier |
| `llx_immo_type_client` | Types de client immobilier | Propriétaire, Locataire, Acheteur, Prospect, Bailleur, Syndic |
| `llx_immo_mode_paiement` | Modes de paiement | Espèces, Virement bancaire, Chèque, Djamo, Orange Money, MTN Mobile Money |
| `llx_immo_type_visite` | Types de visite | Physique, Vidéo |

### 3. Système de droits

| Permission | Description | Modules |
|------------|-------------|---------|
| `immo_read` | Lecture des données immobilières | Tous |
| `immo_write` | Création/modification | Tous |
| `immo_delete` | Suppression/archivage | Tous |
| `immo_admin` | Configuration globale | Core uniquement |
| `immo_quittance_generate` | Générer des quittances | Locatif |
| `immo_bail_resilier` | Résilier un bail | Locatif |
| `immo_mandat_creer` | Créer un mandat de vente | Vente |
| `immo_rapport_voir` | Voir les rapports financiers | Rapports |

### 4. Hooks cadastre (future intégration DGFLTI)

Architecture préparée pour l'intégration du cadastre numérique ivoirien.

| Élément | Description |
|---------|-------------|
| `llx_immo_cadastre_pivot` | Table de liaison bien ↔ parcelle cadastrale |
| `CadastreService` | Service abstrait avec driver |
| `ManualDriver` | Driver actuel (saisie manuelle parcelle_id) |
| `DgfltiDriver` | Driver futur (API DGFLTI) |

### 5. Tables pivot communes

#### `llx_immo_history`
Journal des changements d'état et événements.

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_element | INTEGER | ID de l'élément concerné |
| element_type | VARCHAR(64) | Type d'élément (bien, bail, etc.) |
| action | VARCHAR(64) | Action (create, update, status_change) |
| champ | VARCHAR(64) | Champ modifié |
| ancienne_valeur | TEXT | Valeur avant |
| nouvelle_valeur | TEXT | Valeur après |
| fk_user | INTEGER | Utilisateur ayant fait l'action |
| datec | TIMESTAMP | Date |

## Schéma de base de données

### `llx_immo_config`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| cle | VARCHAR(64) | Clé de configuration |
| valeur | TEXT | Valeur |
| description | VARCHAR(255) | Description |

### `llx_immo_type_bien` (catalogue)

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| code | VARCHAR(32) | Code unique |
| label | VARCHAR(128) | Libellé |
| actif | INTEGER | 1=actif, 0=inactif |

### `llx_immo_etat_bien` (catalogue)

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| code | VARCHAR(32) | Code unique |
| label | VARCHAR(128) | Libellé |
| couleur | VARCHAR(7) | Code couleur hex |
| actif | INTEGER | 1=actif, 0=inactif |

### `llx_immo_type_bail` (catalogue)

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| code | VARCHAR(32) | Code unique |
| label | VARCHAR(128) | Libellé |
| duree_defaut_mois | INTEGER | Durée par défaut |
| actif | INTEGER | 1=actif, 0=inactif |

### `llx_immo_type_client` (catalogue)

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| code | VARCHAR(32) | Code unique |
| label | VARCHAR(128) | Libellé |
| actif | INTEGER | 1=actif, 0=inactif |

### `llx_immo_cadastre_pivot`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_bien | INTEGER | Référence bien |
| parcelle_id | VARCHAR(128) | ID parcelle cadastre (manuel ou DGFLTI) |
| reference_cadastrale | VARCHAR(255) | Référence cadastrale |
| surface_cadastrale | DECIMAL(24,8) | Surface selon cadastre |
| geom_polygon | TEXT | Géométrie GeoJSON (futur) |
| source | VARCHAR(32) | manual, dgflti |
| date_maj | TIMESTAMP | Date mise à jour |

## Interface utilisateur

### Page de configuration
- Formulaire de paramètres globaux
- Tableau d'activation des modules (checkboxes)
- Gestion des catalogues (types de biens, états, etc.)
- Configuration TLPPU (taux par défaut, par commune)

### Menu Dolibarr
```
Immobilier (top menu)
├── Biens
│   ├── Liste
│   ├── Nouveau
│   └── Statistiques
├── Clients
│   ├── Liste
│   ├── Visites
│   └── Prospects
├── Location
│   ├── Baux
│   ├── Quittances
│   └── Échéancier
├── Vente (si activé)
│   ├── Mandats
│   └── Compromis
├── Rénovation (si activé)
│   ├── Chantiers
│   └── Devis
├── Syndic (si activé)
│   ├── Copropriétés
│   └── Appels de fonds
├── Étude de marché (si activé)
│   └── Prix/m²
├── Paiements (si activé)
│   └── Transactions Djamo
└── Rapports (si activé)
    └── Tableau de bord
```

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/config` | Configuration globale |
| PUT | `/api/immo/config` | Modifier configuration |
| GET | `/api/immo/catalog/{type}` | Catalogue (types, etats, etc.) |
| GET | `/api/immo/history` | Journal des événements |

## Dépendances

- **Requis** : `mod_societe`, `mod_user`, `mod_document`
- **Fournit** : Base pour tous les autres modules `mod_immo_*`

## Configuration

Numéro de module : **700000**
Classe : `modImmocore`

## Notes de développement

- Ce module doit être activé en premier. Tous les autres modules dépendent de lui.
- La table `llx_immo_config` peut être utilisée comme key-value store pour les paramètres.
- Les catalogues doivent être peuplés lors de l'activation du module ( données par défaut ivoiriennes).
- Le service `CadastreService` utilise le pattern Strategy pour permettre le switch entre driver manuel et DGFLTI sans changement de code consommateur.
- Prévoir un mécanisme de migration automatique lors des mises à jour de module (table `llx_immo_migrations`).
