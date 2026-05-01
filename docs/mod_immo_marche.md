# Module `mod_immo_marche` — Étude de Marché

## Objectif

Permettre aux agents immobiliers de saisir et suivre les prix de l'immobilier (loyers et ventes) par zone et par type de bien, afin de disposer d'une base de données de comparables et de suivre les tendances du marché.

## Fonctionnalités

### 1. Saisie des comparables

| Champ | Description |
|-------|-------------|
| Date observation | Date de relevé |
| Zone/Quartier | Zone géographique |
| Type de bien | Maison, Appartement, Bureau, etc. |
| Type d'opération | Location ou Vente |
| Surface | m² |
| Prix | Montant |
| Prix au m² | Calculé automatiquement (prix / surface) |
| Source | Observation agent, annonce, transaction réelle |
| Description | Détails (standing, étage, etc.) |

### 2. Tableau de bord marché

| Indicateur | Description |
|------------|-------------|
| Prix moyen au m² | Par zone et par type |
| Évolution prix | Variation sur 6 mois, 1 an |
| Fourchette prix | Min, max, médiane |
| Volume d'observations | Nombre de comparables par zone |

### 3. Export et partage

- Export PDF : rapport d'étude de marché par zone
- Export CSV : données brutes pour analyse externe
- Graphiques : courbes d'évolution, histogrammes

## Schéma de base de données

### `llx_immo_marche_comparable`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence (MARCHE-XXXX) |
| date_observation | DATE | Date du relevé |
| zone | VARCHAR(128) | Zone ou quartier |
| fk_type_bien | INTEGER | Type de bien (catalogue) |
| type_operation | VARCHAR(32) | location, vente |
| surface | DECIMAL(24,8) | Surface en m² |
| prix | DECIMAL(24,8) | Prix observé |
| prix_m2 | DECIMAL(24,8) | Prix au m² (calculé) |
| source | VARCHAR(32) | agent, annonce, transaction |
| description | TEXT | Détails |
| fk_user_creat | INTEGER | Agent ayant saisi |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

## Interface utilisateur

### Saisie rapide
- Formulaire simple (zone, type, surface, prix)
- Calcul auto du prix/m²
- Autocomplétion zone

### Tableau de bord
- Carte des prix par zone (futur : intégration OpenStreetMap)
- Graphique d'évolution par zone/type
- Tableau comparatif

### Export
- Bouton "Générer rapport PDF"
- Bouton "Exporter CSV"

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/marche/comparables` | Liste comparables |
| POST | `/api/immo/marche/comparables` | Ajouter un comparable |
| GET | `/api/immo/marche/stats` | Stats par zone/type |
| GET | `/api/immo/marche/evolution` | Évolution prix dans le temps |

## Dépendances

- **Requis** : `mod_immo_core`

## Configuration

Numéro de module : **700007**
Classe : `modImmomarche`

## Notes de développement

- MVP : Saisie manuelle uniquement
- Évolution : Import CSV, scraping web (sites locaux), API partenaires
- Le prix au m² est calculé automatiquement (trigger SQL ou application)
- Prévoir un index sur (zone, type_bien, type_operation) pour les perfs des stats
