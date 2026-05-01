# Module `mod_immo_vente` — Transactions de Vente

## Objectif

Gérer le cycle complet de vente immobilière : mandat de vente, recherche d'acquéreur, compromis de vente, acte authentique, et calcul des commissions.

## Fonctionnalités

### 1. Mandats de vente

| Onglet | Contenu |
|--------|---------|
| **Informations** | Référence, bien, propriétaire, date début/fin, exclusivité |
| **Conditions** | Prix net vendeur, fourchette de négociation, commission agence |
| **Acquéreur** | Acquéreur final (lien vers client) |
| **Documents** | Mandat signé, compromis, acte notarié |
| **Suivi** | Étapes du processus de vente |

#### Types de mandat

| Type | Description |
|------|-------------|
| Exclusif | L'agence est seule habilitée à vendre |
| Semi-exclusif | L'agence + propriétaire peuvent vendre |
| Simple | Plusieurs agences en concurrence |

### 2. Pipeline de vente

```
Mandat signé → Promotion → Visite → Offre → Négociation → Compromis → Acte notarié → Clôturé
```

| Étape | Description | Durée typique |
|-------|-------------|---------------|
| Mandat signé | Mandat enregistré | J0 |
| Promotion | Publication annonces | J0-J7 |
| Visite | Visites potentiels acquéreurs | J1-J30 |
| Offre | Offre d'achat reçue | J7-J60 |
| Négociation | Discussion prix/conditions | J7-J60 |
| Compromis | Promesse de vente signée | J30-J90 |
| Acte notarié | Signature chez le notaire | J60-J180 |
| Clôturé | Transaction finalisée | J90-J180 |

### 3. Compromis de vente

| Élément | Description |
|---------|-------------|
| Date signature | Date du compromis |
| Prix final | Prix convenu |
| Délai | Délai pour signature acte définitif |
| Conditions suspensives | Obtention prêt, permis, etc. |
| Pénalités | En cas de désistement |

### 4. Calcul des commissions

| Type | Formule | Exemple (prix 50M FCFA) |
|------|---------|-------------------------|
| Commission fixe | Montant forfaitaire | 2 500 000 FCFA |
| Commission % | % du prix de vente | 5% = 2 500 000 FCFA |
| Commission échelonnée | % dégressif selon tranche | 5% jusqu'à 50M, 4% au-delà |

Répartition possible :
- Commission agence : X%
- Commission agent commercial : Y% (sous-commission)

### 5. Frais et taxes

| Frais | Montant | Payé par |
|-------|---------|----------|
| Droit d'enregistrement | 6% du prix | Acheteur |
| TVA (construction neuve) | 18% du prix | Acheteur |
| Frais notariés | ~2-3% | Acheteur |
| Commission agence | Négociable | Vendeur |

## Schéma de base de données

### `llx_immo_mandat_vente`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence (MV-XXXX) |
| fk_bien | INTEGER | Bien à vendre |
| fk_proprietaire | INTEGER | Propriétaire |
| type_mandat | VARCHAR(32) | exclusif, semi, simple |
| date_debut | DATE | Date début mandat |
| date_fin | DATE | Date fin mandat |
| prix_net_vendeur | DECIMAL(24,8) | Prix souhaité |
| prix_minimum | DECIMAL(24,8) | Prix plancher |
| commission_type | VARCHAR(32) | fixe, pourcentage, echelonnee |
| commission_valeur | DECIMAL(24,8) | Valeur commission |
| fk_acquereur | INTEGER | Acquéreur final (si trouvé) |
| statut | VARCHAR(32) | actif, compromis, signe, cloture, expire |
| fk_user_creat | INTEGER | Auteur |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

### `llx_immo_compromis`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence (COMP-XXXX) |
| fk_mandat | INTEGER | Référence mandat |
| fk_acquereur | INTEGER | Acquéreur |
| date_signature | DATE | Date compromis |
| prix_final | DECIMAL(24,8) | Prix convenu |
| delai_signature_jours | INTEGER | Délai acte définitif |
| conditions_suspensives | TEXT | Conditions |
| penalites | TEXT | Pénalités |
| statut | VARCHAR(32) | en_attente, conditions_levees, signe, annule |
| fk_user_creat | INTEGER | Auteur |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

## Interface utilisateur

### Liste des mandats
- Filtres : bien, propriétaire, statut, date expiration
- Colonnes : ref, bien, prix, commission, statut, jours restants
- Alertes : mandat expirant dans 30 jours

### Fiche mandat
- Onglets : Informations, Suivi, Documents, Commission
- Timeline visuelle du pipeline de vente
- Bouton "Créer compromis" quand offre acceptée

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/mandats` | Liste mandats |
| POST | `/api/immo/mandats` | Créer mandat |
| GET | `/api/immo/mandats/{id}` | Détail mandat |
| POST | `/api/immo/mandats/{id}/compromis` | Créer compromis |
| GET | `/api/immo/compromis` | Liste compromis |
| GET | `/api/immo/ventes/stats` | Stats ventes (délai moyen, prix moyen) |

## Dépendances

- **Requis** : `mod_immo_core`, `mod_immo_bien`, `mod_immo_client`
- **Utilise** : `mod_societe`

## Configuration

Numéro de module : **700004**
Classe : `modImmovente`

## Notes de développement

- Le calcul de commission doit être configurable (type, taux, seuils)
- Prévoir un modèle ODT pour le mandat de vente et le compromis
- La timeline du pipeline peut être implémentée via un champ JSON d'étapes ou une table dédiée `llx_immo_vente_etape`
- Alertes automatiques : mandat expirant, compromis dont le délai approche
