# Module `mod_immo_locatif` — Gestion Locative

## Objectif

Gérer l'ensemble du cycle de vie locatif : création des baux, génération des quittances, suivi des échéanciers, calcul automatique des taxes (TLPPU), et paiements.

## Fonctionnalités

### 1. Baux

| Onglet | Contenu |
|--------|---------|
| **Informations** | Référence, bien, locataire, date début/fin, durée |
| **Conditions financières** | Loyer nu, charges, caution, avance, révision |
| **Quittances** | Liste des quittances générées |
| **Indexation** | Taux et dates de révision annuelle |
| **Documents** | Bail signé, état des lieux, cautions |
| **Historique** | Renouvellements, résiliations |

#### Types de bail

| Type | Description | Durée |
|------|-------------|-------|
| Résidentiel vide | Location habitation non meublée | 1 an (renouvelable) |
| Résidentiel meublé | Location meublée | 6 mois |
| Commercial | Local commercial, bureau | 3-6-9 ans |
| Professionnel | Profession libérale | 3 ans |
| Saisonnier | Courte durée | < 6 mois |

#### État d'un bail

```
Brouillon → Actif → En cours de résiliation → Résilié → Archivé
```

### 2. Quittances

Génération automatique mensuelle avec :

| Élément | Description |
|---------|-------------|
| Loyer nu | Montant du loyer de base |
| Charges | Charges récupérables (si applicable) |
| **TLPPU** | Taxe Locale sur la Propriété et la Publicité (calcul auto) |
| Total dû | Loyer + charges + TLPPU |
| Paiement reçu | Montant encaissé |
| Solde | Reste dû ou trop-perçu |

#### Calcul TLPPU

Formule : `TLPPU = Loyer annuel net × Taux communal`

| Commune | Taux indicatif |
|---------|----------------|
| Abidjan (Cocody, Plateau) | 18-20% |
| Abidjan (autres communes) | 15-18% |
| Bouaké, Yamoussoukro | 12-15% |
| Autres villes | 11-13% |

Le taux est configurable par bien (table `llx_immo_bien` → `taux_tlppu`).

### 3. Échéancier

Vue synthétique mensuelle :

| Mois | Loyer dû | TLPPU | Total | Payé | Solde | Statut |
|------|----------|-------|-------|------|-------|--------|
| Jan 2026 | 150 000 | 22 500 | 172 500 | 172 500 | 0 | Payé |
| Fév 2026 | 150 000 | 22 500 | 172 500 | 0 | 172 500 | Impayé |

Alertes :
- Quittance non payée après 5 jours → Alerte agent
- Quittance non payée après 15 jours → Alerte manager + relance automatique email/SMS

### 4. Indexation du loyer

Révision annuelle automatique selon l'indice choisi :

| Indice | Description |
|--------|-------------|
| Libre | Taux fixé par convention |
| ICH (Indice du Coût de l'Habitation) | Indice ivoirien officiel |

Formule : `Nouveau loyer = Ancien loyer × (Index N / Index N-1)`

### 5. Caution et avance

- Enregistrement du montant de la caution (1-3 mois de loyer)
- Suivi de l'utilisation (retenue sur dégâts, remboursement)
- Avance : suivi du nombre de mois payés d'avance

## Schéma de base de données

### `llx_immo_bail`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence bail (BAIL-XXXX) |
| fk_bien | INTEGER | Référence bien |
| fk_locataire | INTEGER | Référence tiers locataire |
| type_bail | VARCHAR(32) | Type (catalogue) |
| date_debut | DATE | Date effet |
| date_fin | DATE | Date fin |
| duree_mois | INTEGER | Durée en mois |
| loyer_nu | DECIMAL(24,8) | Loyer mensuel |
| charges | DECIMAL(24,8) | Charges mensuelles |
| taux_tlppu | DECIMAL(5,2) | Taux TLPPU (%) |
| caution | DECIMAL(24,8) | Montant caution |
| avance | INTEGER | Nombre de mois d'avance |
| indice_indexation | VARCHAR(32) | Type d'indice |
| taux_indexation | DECIMAL(5,2) | Taux max indexation (%) |
| date_prochaine_indexation | DATE | Date prochaine révision |
| statut | VARCHAR(32) | brouillon, actif, resilie, archive |
| fk_user_creat | INTEGER | Auteur |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

### `llx_immo_quittance`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence (QUIT-AAAA-MM-XXXX) |
| fk_bail | INTEGER | Référence bail |
| periode_annee | INTEGER | Année |
| periode_mois | INTEGER | Mois |
| loyer_nu | DECIMAL(24,8) | Loyer nu |
| charges | DECIMAL(24,8) | Charges |
| tlppu | DECIMAL(24,8) | Montant TLPPU |
| total_du | DECIMAL(24,8) | Total dû |
| montant_paye | DECIMAL(24,8) | Montant encaissé |
| solde | DECIMAL(24,8) | Solde (+ = crédit, - = dette) |
| date_paiement | DATE | Date encaissement |
| mode_paiement | VARCHAR(32) | espèces, virement, mobile_money |
| statut | VARCHAR(32) | brouillon, emise, payee_partiel, payee, impayee |
| fk_user_creat | INTEGER | Auteur |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

## Interface utilisateur

### Liste des baux
- Filtres : bien, locataire, statut, date échéance
- Colonnes : ref, bien, locataire, loyer, fin bail, statut
- Actions : voir, générer quittance, résilier

### Fiche bail
- Onglets : Informations, Quittances, Indexation, Documents
- Bouton "Générer quittances du mois" (pour tous les baux)
- Bouton "Générer quittance" (pour ce bail)
- Indicateur visuel du statut de paiement

### Échéancier global
- Vue mensuelle de tous les baux
- Total des loyers attendus vs encaissés
- Taux d'encaissement (%)

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/baux` | Liste des baux |
| POST | `/api/immo/baux` | Créer un bail |
| GET | `/api/immo/baux/{id}` | Détail bail |
| PUT | `/api/immo/baux/{id}` | Modifier bail |
| GET | `/api/immo/baux/{id}/quittances` | Quittances du bail |
| POST | `/api/immo/baux/{id}/quittances` | Générer quittance |
| GET | `/api/immo/quittances` | Liste quittances (filtrable par mois) |
| POST | `/api/immo/quittances/{id}/paiement` | Enregistrer paiement |
| GET | `/api/immo/echeancier` | Échéancier global |

## Dépendances

- **Requis** : `mod_immo_core`, `mod_immo_bien`, `mod_immo_client`
- **Utilise** : `mod_societe` (tiers), `mod_document`

## Configuration

Numéro de module : **700003**
Classe : `modImmolocatif`

## Notes de développement

- La génération de quittances doit pouvoir être massive (tous les baux actifs d'un coup)
- Le calcul TLPPU doit être paramétrable par bien (taux par défaut dans la config, surchargeable)
- Prévoir un modèle de document ODT/DOCX pour l'impression des quittances
- Les quittances doivent être numérotées de manière continue pour la comptabilité
- Intégration comptable : génération d'écritures dans le module Comptabilité Dolibarr (futur)
