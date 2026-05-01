# Module `mod_immo_client` — CRM Immobilier

## Objectif

Gérer l'ensemble des relations avec les tiers immobiliers : propriétaires, locataires, acheteurs, prospects. Centraliser les contacts, visites, et historique des interactions.

## Fonctionnalités

### 1. Typologie des tiers immobiliers

Un tiers Dolibarr standard peut avoir plusieurs "casquettes" immobilières :

| Type | Code | Description |
|------|------|-------------|
| Propriétaire | `PROPRIETAIRE` | Dépose un bien à louer ou vendre |
| Locataire | `LOCATAIRE` | Occupe un bien en location |
| Acheteur | `ACHETEUR` | En recherche d'achat |
| Prospect | `PROSPECT` | Contact potentiel, pas encore actif |
| Bailleur | `BAILLEUR` | Propriétaire institutionnel |
| Syndic mandataire | `SYNDIC` | Gère une copropriété |

Un même tiers peut être à la fois **Propriétaire** et **Locataire** (propriétaire d'un bien qu'il loue ailleurs).

### 2. Fiche client immobilier

Extension de la fiche tiers Dolibarr avec onglet "Immobilier" :

| Section | Contenu |
|---------|---------|
| **Rôle(s)** | Propriétaire, Locataire, Acheteur, Prospect (checkboxes) |
| **Biens associés** | Liste des biens liés avec type de relation |
| **Baux** | Baux en cours et historique (si locataire) |
| **Mandats** | Mandats de vente en cours (si propriétaire) |
| **Visites** | Historique des visites effectuées/programmées |
| **Documents** | Pièce d'identité, contrats, quittances |
| **Notes** | Commentaires et suivis commerciaux |

### 3. Gestion des visites

| Champ | Description |
|-------|-------------|
| Date et heure | Visite programmée |
| Bien visité | Lien vers `llx_immo_bien` |
| Client/Prospect | Lien vers tiers |
| Agent responsable | Lien vers utilisateur Dolibarr |
| Type de visite | Physique, Vidéo (Visioconférence) |
| Statut | Planifiée, Effectuée, Annulée, Reportée |
| Commentaire | Retour de visite |
| Suivi | Intérêt confirmé, négociation, refus |

### 4. Recherche et matching

- Recherche de biens correspondant aux critères d'un prospect (budget, zone, type)
- Alertes automatiques : nouveau bien correspondant aux critères d'un prospect
- Liste des prospects par critère de recherche

### 5. Pipeline commercial

```
Prospect → Contact établi → Visite programmée → Visite effectuée
                                                  ↓
                            Offre faite → Négociation → Acceptée → Signée
                                                  ↓
                                               Refusée → Relance
```

## Schéma de base de données

### `llx_immo_client_type`
Table pivot : un tiers peut avoir plusieurs types.

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_soc | INTEGER | Référence tiers |
| type_client | VARCHAR(32) | Type (catalogue) |
| date_debut | DATE | Date début relation |
| date_fin | DATE | Date fin relation |
| status | INTEGER | Actif/Inactif |

### `llx_immo_visite`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| ref | VARCHAR(128) | Référence visite (VIS-XXXX) |
| fk_bien | INTEGER | Bien visité |
| fk_soc | INTEGER | Prospect/Client |
| fk_user | INTEGER | Agent responsable |
| date_visite | DATETIME | Date et heure |
| type_visite | VARCHAR(32) | physique, video |
| statut | VARCHAR(32) | planifiee, effectuee, annulee, reportee |
| commentaire | TEXT | Retour de visite |
| suivi | VARCHAR(32) | interet, negociation, offre, refuse |
| rappel | DATE | Date de relance |
| fk_user_creat | INTEGER | Auteur |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

## Interface utilisateur

### Liste des clients immobiliers
- Filtres : type (propriétaire, locataire...), zone, statut
- Colonnes : nom, type(s), téléphone, email, nombre de biens, dernière activité

### Agenda des visites
- Vue calendrier (jour/semaine/mois)
- Drag & drop pour reprogrammer
- Couleur par statut

### Matching prospect/bien
- Formulaire de recherche multi-critères
- Résultats avec score de correspondance
- Bouton "Envoyer la sélection par email"

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/clients` | Liste des clients immobiliers |
| POST | `/api/immo/clients/{socid}/types` | Ajouter un type à un tiers |
| GET | `/api/immo/visites` | Liste des visites |
| POST | `/api/immo/visites` | Planifier une visite |
| PUT | `/api/immo/visites/{id}` | Modifier une visite |
| GET | `/api/immo/matching` | Matching prospect/biens |
| GET | `/api/immo/clients/{socid}/baux` | Baux du client |

## Dépendances

- **Requis** : `mod_immo_core`, `mod_societe`
- **Utilisé par** : `mod_immo_locatif`, `mod_immo_vente`, `mod_immo_syndic`

## Configuration

Numéro de module : **700002**
Classe : `modImmoclient`

## Notes de développement

- Étendre la fiche tiers Dolibarr via un hook `formObjectOptions` (onglet supplémentaire)
- La recherche de matching peut être implémentée via une requête SQL avec scoring simple (surface, prix, zone)
- Prévoir une notification email pour les visites programmées (24h avant)
