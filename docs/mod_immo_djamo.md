# Module `mod_immo_djamo` — Intégration Paiement Djamo

## Objectif

Intégrer la solution de paiement mobile **Djamo** pour permettre l'encaissement des loyers, le suivi des transactions, et la réconciliation automatique avec les quittances.

## Fonctionnalités

### 1. Configuration Djamo

| Paramètre | Description |
|-----------|-------------|
| API Key | Clé API Djamo |
| API Secret | Secret associé |
| Mode | Sandbox / Production |
| Devise | XOF |
| Compte receveur | ID compte Djamo de l'agence |

### 2. Génération de requête de paiement

Pour chaque quittance impayée, génération d'un QR code ou d'un lien de paiement Djamo contenant :

| Élément | Description |
|---------|-------------|
| Montant | Total dû (loyer + charges + TLPPU) |
| Référence | Numéro de quittance |
| Description | "Quittance loyer [Mois] [Année] - [Adresse bien]" |
| Expiration | Date limite de paiement |

### 3. Suivi des transactions

| Statut transaction | Description |
|-------------------|-------------|
| `pending` | En attente de paiement |
| `processing` | Traitement en cours |
| `completed` | Paiement réussi |
| `failed` | Échec |
| `refunded` | Remboursé |

### 4. Webhook Djamo

Réception des notifications de changement de statut via webhook :

```json
{
  "event": "payment.completed",
  "data": {
    "reference": "QUIT-2026-01-0001",
    "amount": 172500,
    "currency": "XOF",
    "status": "completed",
    "paid_at": "2026-01-05T10:30:00Z",
    "payment_method": "djamo_wallet"
  }
}
```

### 5. Réconciliation automatique

Lorsqu'un webhook "completed" est reçu :
1. Recherche de la quittance par référence
2. Mise à jour du statut de la quittance (`payee`)
3. Enregistrement du montant payé et de la date
4. Notification à l'agent responsable

## Schéma de base de données

### `llx_immo_djamo_config`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| cle | VARCHAR(64) | Clé config |
| valeur | TEXT | Valeur |

### `llx_immo_djamo_transaction`

| Champ | Type | Description |
|-------|------|-------------|
| rowid | SERIAL PK | ID |
| fk_quittance | INTEGER | Référence quittance |
| djamo_reference | VARCHAR(255) | Référence transaction Djamo |
| montant | DECIMAL(24,8) | Montant |
| statut | VARCHAR(32) | pending, completed, failed, refunded |
| date_paiement | TIMESTAMP | Date de paiement |
| mode_paiement | VARCHAR(64) | wallet, card, mobile_money |
| raw_webhook | JSONB | Payload webhook brut |
| datec | TIMESTAMP | Date création |
| tms | TIMESTAMP | Date modification |

## Interface utilisateur

### Configuration
- Page de paramètres Djamo (clés API, mode)
- Test de connexion à l'API

### Quittance
- Bouton "Payer avec Djamo" sur chaque quittance impayée
- Affichage QR code (ou lien)
- Historique des paiements Djamo

### Transactions
- Liste des transactions Djamo
- Filtres : statut, date, montant
- Bouton "Relancer" pour les impayés

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/immo/djamo/config` | Configurer Djamo |
| POST | `/api/immo/djamo/quittances/{id}/payer` | Créer requête de paiement |
| POST | `/api/immo/djamo/webhook` | Réception webhook Djamo |
| GET | `/api/immo/djamo/transactions` | Liste transactions |

## Dépendances

- **Requis** : `mod_immo_core`, `mod_immo_locatif`
- **Utilise** : API REST Djamo

## Configuration

Numéro de module : **700008**
Classe : `modImmodjamo`

## Notes de développement

- L'intégration Djamo nécessite un compte professionnel et des credentials API
- Le webhook doit être sécurisé (signature/vérification token)
- Prévoir un mode "sandbox" pour les tests sans vrais paiements
- La réconciliation doit être idempotente (traitement multiple du même webhook sans doublon)
- Le module peut être étendu pour d'autres moyens de paiement (Orange Money, MTN Mobile Money) via le même pattern
