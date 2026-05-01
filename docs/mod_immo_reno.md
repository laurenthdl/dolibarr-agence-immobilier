# Module `mod_immo_reno` — Suivi des Rénovations

## Objectif

Suivre les travaux de rénovation des biens avant leur mise sur le marché (location ou vente). Gestion des devis, budgets, avancement, et changement d'état du bien.

## Fonctionnalités

### 1. Fiche chantier de rénovation

| Onglet | Contenu |
|--------|---------|
| **Informations** | Référence, bien concerné, date début/fin prévue |
| **Budget** | Budget prévisionnel, consommé, restant |
| **Travaux** | Liste des postes de travaux |
| **Fournisseurs** | Entreprises/artisans intervenants |
| **Documents** | Devis, factures, photos avant/après |
| **Avancement** | Taux global et par poste |

### 2. Postes de travaux

| Poste | Description | Unité |
|-------|-------------|-------|
| Maçonnerie | Murs, fondations | Forfait |
| Plomberie | Installation eau | Forfait |
| Électricité | Câblage, tableaux | Forfait |
| Peinture | Intérieur/extérieur | m² |
| Menuiserie | Portes, fenêtres | Forfait |
| Carrelage | Sols, murs | m² |
| Toiture | Réparation/remplacement | m² |
| Aménagement | Cuisine, sanitaires | Forfait |

### 3. Suivi budgétaire

| Élément | Description |
|---------|-------------|
| Budget prévisionnel | Somme des devis |
| Budget consommé | Somme des factures payées |
| Budget restant | Prévisionnel - Consommé |
| Écart | Consommé - Prévisionnel (alerte si > 10%) |

### 4. Changement d'état du bien

Lorsque les travaux sont terminés, le bien passe automatiquement de l'état **En rénovation** à **Disponible** (ou **À louer** / **À vendre** selon la destination).

```
Bien (À rénover) → Chantier créé → Travaux en cours → Travaux terminés → Bien (Disponible)
```

## Schéma de base de données

### `llx_immo_reno_chantier`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence (RENO-XXXX) |
| fk_bien | INTEGER | Bien rénové |
| date_debut_prevue | DATE | Date début prévue |
| date_fin_prevue | DATE | Date fin prévue |
| date_debut_reelle | DATE | Date début réelle |
| date_fin_reelle | DATE | Date fin réelle |
| budget_prevu | DECIMAL(24,8) | Budget total |
| budget_consomme | DECIMAL(24,8) | Budget consommé |
| avancement_global | INTEGER | % avancement (0-100) |
| statut | VARCHAR(32) | planifie, en_cours, termine, annule |
| fk_user_creat | INTEGER | Auteur |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

### `llx_immo_reno_poste`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_chantier | INTEGER | Référence chantier |
| type_poste | VARCHAR(64) | Type de travaux |
| description | TEXT | Description |
| budget_prevu | DECIMAL(24,8) | Budget poste |
| budget_consomme | DECIMAL(24,8) | Budget consommé |
| avancement | INTEGER | % avancement |
| fk_soc_fournisseur | INTEGER | Fournisseur/artisan |
| statut | VARCHAR(32) | a_faire, en_cours, termine |

## Interface utilisateur

### Liste des chantiers
- Filtres : bien, statut, fourchette budget
- Colonnes : ref, bien, budget, avancement, statut

### Fiche chantier
- Onglets : Informations, Postes de travaux, Budget, Documents, Photos
- Barre de progression visuelle de l'avancement global
- Comparaison budget prévu vs consommé (graphique)

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/renovations` | Liste chantiers |
| POST | `/api/immo/renovations` | Créer chantier |
| GET | `/api/immo/renovations/{id}` | Détail chantier |
| POST | `/api/immo/renovations/{id}/postes` | Ajouter un poste |
| PUT | `/api/immo/renovations/{id}/avancement` | Mettre à jour avancement |
| GET | `/api/immo/renovations/stats` | Stats rénovations (coût moyen/m²) |

## Dépendances

- **Requis** : `mod_immo_core`, `mod_immo_bien`
- **Utilise** : `mod_societe` (fournisseurs)

## Configuration

Numéro de module : **700005**
Classe : `modImmoreno`

## Notes de développement

- Le changement d'état du bien à la fin du chantier peut être automatisé via un trigger ou un workflow
- Prévoir une galerie photos avant/après par chantier
- Le budget peut être lié au module Comptabilité Dolibarr pour le suivi comptable
