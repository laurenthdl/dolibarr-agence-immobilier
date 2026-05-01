# Module `mod_immo_bien` — Gestion des Biens

## Objectif

Centraliser la gestion de tous les biens immobiliers de l'agence : fiche descriptive, typologie, photos, documents légaux, géolocalisation et suivi d'état.

## Fonctionnalités

### 1. Fiche bien

| Onglet | Contenu |
|--------|---------|
| **Informations générales** | Référence, libellé, typologie, état, adresse complète |
| **Caractéristiques** | Surface habitable, surface terrain, nombre de pièces, nombre d'étages |
| **Géolocalisation** | Latitude, longitude, zone/quartier, commune |
| **Propriétaire** | Lien vers tiers Dolibarr (via `llx_immo_bien_client`) |
| **Photos & Documents** | Titre foncier, plan, photos, autres documents |
| **Historique** | Changements d'état, rénovations, ventes, locations |
| **Notes** | Commentaires chronologiques |

### 2. Typologie des biens

| Type | Description | Champs spécifiques |
|------|-------------|-------------------|
| Maison | Villa, duplex, triplex | Jardin, garage, piscine |
| Appartement | Résidentiel | Étage, ascenseur, parking |
| Bureau | Commercial | Open-space, salles de réunion |
| Boutique | Local commercial | Vitrine, arrière-boutique |
| Entrepôt | Stockage | Hauteur sous plafond, quai |
| Terrain | Nu ou bâti | Viabilisé, superficie |
| Immeuble | R+1 à R+N | Nombre d'appartements, ascenseur |

### 3. États d'un bien

```
À acquérir → Disponible → À rénover → En rénovation → À louer / À vendre
                                    ↓
                              Loué / Vendu → Archivé
```

| État | Code | Description |
|------|------|-------------|
| À acquérir | `A_ACQUERIR` | Bien identifié, pas encore propriété de l'agence |
| Disponible | `DISPONIBLE` | Prêt à être loué ou vendu |
| À rénover | `A_RENOVER` | Nécessite des travaux avant mise sur le marché |
| En rénovation | `EN_RENOVATION` | Travaux en cours (lien module `immo_reno`) |
| À louer | `A_LOUER` | Mis en location |
| Loué | `LOUE` | Bail en cours |
| À vendre | `A_VENDRE` | Mis en vente |
| Vendu | `VENDU` | Transaction finalisée |
| Archivé | `ARCHIVE` | Plus dans le portefeuille actif |

### 4. Géolocalisation

- Saisie manuelle ou géocodage via OpenStreetMap Nominatim
- Affichage carte (Leaflet) sur la fiche bien
- Filtrage par zone/quartier/commune
- Distance depuis un point (futur)

### 5. Documents associés

| Type | Obligatoire | Description |
|------|-------------|-------------|
| Titre foncier | Oui | Document de propriété |
| Plan | Non | Plan de masse, plan intérieur |
| Photo | Non | Photos du bien (illimitées) |
| Diagnostic | Non | État des lieux, DPE équivalent |
| Devis travaux | Non | Lien module `immo_reno` |

## Schéma de base de données

### `llx_immo_bien`
| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID technique |
| ref | VARCHAR(128) | Référence unique (IMMO-XXXX) |
| label | VARCHAR(255) | Libellé du bien |
| fk_soc_proprietaire | INTEGER | Référence tiers propriétaire |
| type_bien | VARCHAR(64) | Type (catalogue immocore) |
| etat | VARCHAR(32) | État actuel |
| adresse | VARCHAR(255) | Adresse |
| cp | VARCHAR(32) | Code postal/zone |
| ville | VARCHAR(128) | Ville/Commune |
| pays | VARCHAR(2) | Code pays (ISO) |
| latitude | DECIMAL(10,8) | Latitude |
| longitude | DECIMAL(11,8) | Longitude |
| superficie_habitable | DECIMAL(24,8) | m² habitable |
| superficie_terrain | DECIMAL(24,8) | m² terrain |
| nombre_pieces | INTEGER | Nombre de pièces |
| nombre_etages | INTEGER | Nombre d'étages |
| etage | INTEGER | Étage (pour appartement) |
| caracteristiques | TEXT | JSON des caractéristiques spécifiques |
| description | TEXT | Description libre |
| prix_achat | DECIMAL(24,8) | Prix d'achat (si applicable) |
| prix_location | DECIMAL(24,8) | Loyer mensuel cible |
| prix_vente | DECIMAL(24,8) | Prix de vente cible |
| fk_user_creat | INTEGER | Auteur création |
| fk_user_modif | INTEGER | Auteur modification |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |
| status | INTEGER | Statut Dolibarr (0=draft, 1=validated) |

### `llx_immo_bien_caracteristique`
| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_bien | INTEGER | Référence bien |
| cle | VARCHAR(64) | Clé (garage, piscine, ascenseur, etc.) |
| valeur | VARCHAR(255) | Valeur |

## Interface utilisateur

### Liste des biens
- Filtres : type, état, commune, propriétaire, fourchette prix
- Colonnes : ref, photo miniature, adresse, type, état, prix
- Actions rapides : voir, modifier, dupliquer, archiver

### Fiche bien
- Onglets : Informations, Caractéristiques, Propriétaire, Photos/Documents, Historique, Notes
- Bouton "Créer un bail" (si locatif activé)
- Bouton "Créer un mandat de vente" (si vente activé)
- Bouton "Lancer des travaux" (si rénovation activé)

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/immo/biens` | Liste des biens (filtrable) |
| POST | `/api/immo/biens` | Créer un bien |
| GET | `/api/immo/biens/{id}` | Détail d'un bien |
| PUT | `/api/immo/biens/{id}` | Modifier un bien |
| DELETE | `/api/immo/biens/{id}` | Archiver un bien |
| GET | `/api/immo/biens/{id}/documents` | Documents associés |
| POST | `/api/immo/biens/{id}/documents` | Ajouter un document |
| GET | `/api/immo/biens/{id}/history` | Historique des états |

## Dépendances

- **Requis** : `mod_immo_core`
- **Utilise** : `mod_societe` (tiers), `mod_document` (documents)
- **Utilisé par** : `mod_immo_locatif`, `mod_immo_vente`, `mod_immo_reno`, `mod_immo_syndic`

## Configuration

Numéro de module : **700001**
Classe : `modImmobien`

## Notes de développement

- La référence doit être générée automatiquement (format : `IMMO-AAAA-XXXX`)
- Les changements d'état doivent être loggés dans `llx_immo_history`
- Le champ `caracteristiques` en JSON permet l'extensibilité par type de bien
- Prévoir un champ `entity` pour le multi-company
