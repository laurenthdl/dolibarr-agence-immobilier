# Module `mod_immo_rapports` — Tableaux de Bord et Rapports

## Objectif

Fournir une vision synthétique et décisionnelle de l'activité immobilière : indicateurs clés (KPIs), taux d'occupation, rentabilité, impayés, et exports.

## Fonctionnalités

### 1. Tableau de bord principal

| Widget | Description |
|--------|-------------|
| **Taux d'occupation** | % de biens loués vs total géré |
| **Loyers encaissés (mois)** | Total perçu ce mois |
| **Impayés** | Montant total des quittances impayées |
| **Biens disponibles** | Nombre de biens à louer/vendre |
| **Rentabilité globale** | (Loyers perçus - Charges) / Valeur portefeuille |
| **Délai moyen location** | Temps moyen entre disponibilité et location |
| **Délai moyen vente** | Temps moyen entre mandat et compromis |

### 2. Rapports détaillés

| Rapport | Contenu | Période |
|---------|---------|---------|
| **Situation locative** | Baux actifs, quittances, impayés | Mensuel |
| **Situation ventes** | Mandats, compromis, commissions | Mensuel/Trimestriel |
| **Rentabilité par bien** | Recettes, charges, marge | Annuel |
| **Évolution marché** | Prix/m², volumes | Trimestriel |
| **Activité agents** | Visites, baux signés, ventes | Mensuel |

### 3. Exports

| Format | Contenu |
|--------|---------|
| PDF | Rapport formaté avec graphiques |
| CSV | Données brutes pour Excel |
| Excel | Feuille calculée avec formules |

### 4. Alertes

| Alerte | Déclencheur |
|--------|-------------|
| Quittance impayée | > 5 jours après échéance |
| Bail expirant | < 60 jours avant fin |
| Mandat expirant | < 30 jours avant fin |
| Délai location long | Bien disponible > 60 jours |
| Délai vente long | Mandat > 90 jours sans offre |

## Schéma de base de données

Ce module est principalement en **lecture**. Il s'appuie sur les tables des autres modules.

### `llx_immo_rapport_favori`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_user | INTEGER | Utilisateur |
| nom_rapport | VARCHAR(128) | Nom du rapport |
| filtres | JSONB | Filtres sauvegardés |
| periode_defaut | VARCHAR(32) | jour, semaine, mois, annee |

## Interface utilisateur

### Dashboard
- Grille de widgets configurables
- Filtres rapides : agence globale, par bien, par période

### Rapports
- Liste des rapports disponibles
- Sélection période (date picker)
- Prévisualisation + export

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/rapports/dashboard` | Données dashboard |
| GET | `/api/immo/rapports/location` | Rapport location |
| GET | `/api/immo/rapports/vente` | Rapport ventes |
| GET | `/api/immo/rapports/rentabilite` | Rentabilité par bien |
| GET | `/api/immo/rapports/export/{format}` | Export (pdf, csv) |

## Dépendances

- **Requis** : `mod_immo_core`
- **Utilise** : Toutes les tables des autres modules (`bien`, `locatif`, `vente`, `reno`, `syndic`, `djamo`)

## Configuration

Numéro de module : **700009**
Classe : `modImmorapports`

## Notes de développement

- Les widgets du dashboard peuvent être implémentés via des requêtes SQL agrégées
- Les graphiques peuvent utiliser une librairie JS comme Chart.js intégrée dans Dolibarr
- Les exports PDF peuvent utiliser les mêmes moteurs de template que Dolibarr (ODT → PDF via LibreOffice)
- Les alertes peuvent être envoyées par email ou affichées dans le tableau de bord Dolibarr
- Prévoir la mise en cache des données dashboard (refresh toutes les heures) pour les perfs
