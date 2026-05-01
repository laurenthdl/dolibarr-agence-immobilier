# Guide Utilisateur — Gestion Agence Immobilière Côte d'Ivoire

> Version 1.0 | Dolibarr 23.x | Modules `700000` — `700009`
> **Public cible** : Agents commerciaux, Gestionnaires locatifs, Comptables, Directeurs d'agence

---

## Table des matières

1. [Biens immobiliers](#1-biens-immobiliers)
2. [Clients et CRM](#2-clients-et-crm)
3. [Gestion locative](#3-gestion-locative)
4. [Transactions de vente](#4-transactions-de-vente)
5. [Rénovation](#5-rénovation)
6. [Syndic de copropriété](#6-syndic-de-copropriété)
7. [Étude de marché](#7-étude-de-marché)
8. [Paiement mobile Djamo](#8-paiement-mobile-djamo)
9. [Rapports et tableaux de bord](#9-rapports-et-tableaux-de-bord)

---

## 1. Biens immobiliers

### 1.1 Créer un bien

1. Menu `Immobilier > Biens > Nouveau`
2. Renseigner :
   - **Référence** : générée automatiquement (`BYYYY-NNNN`, ex: `B2026-0042`)
   - **Type** : sélectionner dans le catalogue (Maison, Appartement, Bureau, Boutique, Entrepôt, Terrain)
   - **Adresse** : localisation géographique complète
   - **Surface** : superficie en m²
   - **Taux TLPPU** : pourcentage spécifique au bien (si vide, prend la valeur par défaut de la configuration)
   - **État** : Disponible, À louer, Loué, À vendre, Vendu, En rénovation, etc.
3. Cliquer sur **Enregistrer**

> Le bien est créé à l'état **Brouillon** et doit être validé pour être visible par les agents.

### 1.2 Modifier un bien

Sur la fiche d'un bien :
- Bouton **Modifier** pour changer les caractéristiques
- Menu déroulant **État** pour changer le statut (utile lorsqu'un bien passe de "À louer" à "Loué")

### 1.3 Actions disponibles

| Action | Description | Qui peut le faire |
|--------|-------------|-------------------|
| **Modifier** | Changer les caractéristiques, l'état | Gestionnaire, Agent |
| **Dupliquer** | Créer un bien similaire (utile pour immeubles avec plusieurs lots) | Gestionnaire |
| **Supprimer** | Suppression logique (le bien reste en base, marqué comme supprimé) | Administrateur |
| **Ajouter document** | Joindre photos, plans, diagnostics, pdf | Tout utilisateur |
| **Historique** | Voir les changements d'état (quand et par qui) | Tout utilisateur |

### 1.4 Cycle de vie d'un bien

Un bien traverse les états suivants au cours de son existence :

```
À acquérir → Disponible → À louer / À vendre → Loué / Vendu → Archivé
                ↑___________________________________________↓
                              (renouvellement ou remise sur le marché)
```

| État | Signification | Action possible |
|------|---------------|-----------------|
| **À acquérir** | L'agence n'est pas encore propriétaire/gérante | Créer fiche prévisionnelle |
| **Disponible** | Le bien est prêt à être mis sur le marché | Changer vers "À louer" ou "À vendre" |
| **À louer** | Le bien est proposé à la location | Créer un bail, programmer des visites |
| **À vendre** | Le bien est proposé à la vente | Créer un mandat, programmer des visites |
| **Loué** | Un bail actif est en cours | Générer quittances, suivre paiements |
| **Vendu** | Une vente est finalisée | Archiver le bien |
| **Archivé** | Le bien n'est plus géré par l'agence | Consultation uniquement |

---

## 2. Clients et CRM

### 2.1 Créer un tiers immobilier

1. Menu `Immobilier > Clients > Nouveau`
2. Choisir le **type** dans le catalogue :
   - **Propriétaire** : personne possédant un bien confié à l'agence
   - **Locataire** : personne occupant un bien en location
   - **Acheteur** : personne intéressée par un achat
   - **Prospect** : contact potentiel, pas encore engagé
   - **Bailleur** : investisseur gérant plusieurs biens
3. Renseigner :
   - Nom, prénom ou raison sociale
   - Coordonnées (email, téléphone)
   - **Numéro de téléphone** : essentiel pour l'envoi de liens de paiement Djamo
   - Adresse
4. Cliquer sur **Enregistrer**

> La fiche client est liée au module `Société` natif de Dolibarr, enrichie de champs immobiliers.

### 2.2 Suivi des visites

1. Sur la fiche d'un **bien** ou d'un **client**, onglet **Visites**
2. Bouton **Nouvelle visite** :
   - Date et heure
   - **Type** : Physique (sur place) ou Vidéo (visite virtuelle)
   - Commentaire : appréciation du bien, points à vérifier
3. Statuts possibles :
   - **Planifiée** → **Effectuée** → **Réussie** ou **Echouée**

> Les visites ayant le statut "Réussie" peuvent déclencher automatiquement la création d'un bail (si le client est un locataire) ou d'un mandat de vente (si le client est un acheteur).

---

## 3. Gestion locative

### 3.1 Créer un bail

1. Menu `Immobilier > Location > Baux > Nouveau**
2. Sélectionner :
   - **Bien** : uniquement parmi les biens à l'état "Disponible" ou "À louer"
   - **Locataire** : tiers de type "Locataire"
   - **Type de bail** : Résidentiel vide, Résidentiel meublé, Commercial, Professionnel, Saisonnier
3. Renseigner les conditions financières :
   - **Loyer nu mensuel** (ex: 150 000 FCFA)
   - **Charges mensuelles** (si le bail inclut des charges récupérables)
   - **Taux TLPPU** : pourcentage de la Taxe Locale sur la Propriété ; pris par défaut depuis le bien, modifiable
   - **Caution** : montant exigé (généralement 1 à 3 mois de loyer)
   - **Avance** : nombre de mois payés d'avance (généralement 1 à 3 mois)
4. Dates :
   - **Date de début** : date d'effet du bail
   - **Date de fin** : date de fin (calculée automatiquement selon le type de bail)
5. Cliquer sur **Enregistrer**

> Le bail est créé à l'état **Brouillon**. Il doit être validé pour activer le bien.

### 3.2 Valider un bail

Sur la fiche du bail :
1. Vérifier que toutes les informations sont correctes
2. Bouton **Valider**
3. La date de validation est enregistrée
4. Le bien concerné passe automatiquement à l'état **Loué**

Le bail est maintenant **actif** et prêt pour la génération de quittances.

### 3.3 Générer les quittances

Deux modes de génération sont disponibles :

#### A. Quittance unique (pour un bail spécifique)

1. Ouvrir la fiche du bail
2. Onglet **Quittances**
3. Bouton **Générer quittance du mois**
4. Sélectionner le **mois** et l'**année**
5. Cliquer sur **Valider**

La quittance est créée avec calcul automatique de tous les postes :
- Loyer nu (montant mensuel)
- Charges (si applicable)
- **TLPPU** calculé : `Loyer nu × Taux communal / 100`

#### B. Génération massive (tous les baux actifs)

1. Menu `Immobilier > Location > Quittances`
2. Bouton **Générer quittances du mois**
3. Sélectionner le **mois** et l'**année**
4. Le système affiche la liste des baux concernés avec le montant total
5. Cliquer sur **Valider** pour générer toutes les quittances en une seule opération

> **Important** : La génération massive ne crée pas de quittance pour les baux déjà ayant une quittance pour le mois sélectionné.

### 3.4 Exemple de calcul TLPPU (Taxe Locale sur la Propriété et la Publicité)

| Élément | Montant | Commentaire |
|---------|---------|-------------|
| Loyer nu mensuel | 150 000 FCFA | Montant du contrat |
| Charges mensuelles | 10 000 FCFA | Charges récupérables |
| Taux TLPPU (Cocody) | 15% | Fixé sur le bien ou valeur par défaut |
| **TLPPU mensuelle** | 150 000 × 15% = **22 500 FCFA** | Calcul automatique |
| **Total dû** | 150 000 + 10 000 + 22 500 = **182 500 FCFA** | Somme des postes |

> Le taux TLPPU varie selon les communes : 11-13% pour les villes secondaires, 15-18% pour Abidjan, 18-20% pour Cocody et Plateau.

### 3.5 Enregistrer un paiement

Sur la fiche d'une quittance :
1. Bouton **Enregistrer un paiement**
2. Saisir :
   - **Montant payé** (peut être inférieur au total dû = paiement partiel)
   - **Date de paiement**
   - **Mode de paiement** : Espèces, Virement bancaire, Chèque, Djamo, Orange Money, MTN Mobile Money
3. Optionnel : commentaire
4. Cliquer sur **Valider**

Le **solde** est calculé automatiquement : `Total dû - Montant payé`
- Si solde = 0 : statut passe à **Payée**
- Si solde > 0 et un paiement existe : statut **Payée partiellement**
- Si aucun paiement : statut **Émise** (puis **Impayée** après délai)

### 3.6 Consulter l'échéancier

Menu `Immobilier > Location > Échéancier` :

L'échéancier affiche une vue mensuelle synthesizant tous les baux actifs.

| Colonne | Signification |
|---------|---------------|
| Mois | Période (ex: Jan 2026) |
| Loyer dû | Total des loyers attendus |
| TLPPU | Total des taxes calculées |
| Total | Somme totale à percevoir |
| Payé | Montant réellement encaissé |
| Solde | Reste dû ou trop-perçu |
| Statut | Couleur d'alerte |

**Codes couleur** :
- **Vert** : payé intégralement
- **Orange** : payé partiellement
- **Rouge** : impayé

**Alertes automatiques** :
- +5 jours après échéance : notification à l'agent gestionnaire
- +15 jours après échéance : notification au manager + relance email/SMS automatique

### 3.7 Résilier un bail

1. Ouvrir la fiche du bail
2. Bouton **Résilier**
3. Saisir :
   - **Date de résiliation effective** (peut être future)
   - **Motif** : fin de bail naturelle, impayés récurrents, mutation professionnelle, etc.
4. Cliquer sur **Confirmer**

Le bien repasse automatiquement à l'état **Disponible**.
> Si des quittances impayées existent, elles restent visibles dans l'échéancier.

### 3.8 Indexation annuelle du loyer

1. Fiche bail > onglet **Indexation**
2. Sélectionner l'**indice** :
   - **ICH** (Indice du Coût de l'Habitation) : indice officiel ivoirien
   - **Taux libre** : taux fixé par convention dans le bail
3. Saisir :
   - **Ancien indice** (valeur au dernier révision)
   - **Nouvel indice** (valeur actuelle)
4. Le calcul est automatique :
   ```
   Nouveau loyer = Ancien loyer × (Index N / Index N-1)
   ```
5. Cliquer sur **Appliquer**

> La date de prochaine indexation est automatiquement incrémentée d'un an.

---

## 4. Transactions de vente

### 4.1 Créer un mandat de vente

1. Menu `Immobilier > Vente > Mandats > Nouveau**
2. Sélectionner :
   - **Bien** : le bien à vendre (doit être à l'état "À vendre" ou "Disponible")
   - **Propriétaire** : tiers vendeur (type "Propriétaire" ou "Bailleur")
3. Renseigner :
   - **Type de mandat** :
     - **Exclusif** : l'agence est seule habilitée à vendre
     - **Semi-exclusif** : l'agence et le propriétaire peuvent vendre
     - **Simple** : plusieurs agences en concurrence
   - **Prix net vendeur** : prix souhaité par le propriétaire (ex: 50 000 000 FCFA)
   - **Prix minimum** : plancher de négociation
   - **Commission** :
     - Type : Fixe, Pourcentage, Échelonnée
     - Valeur : ex: 5% ou 2 500 000 FCFA fixe
4. Dates :
   - **Date de début** : signature du mandat
   - **Date de fin** : expiration (alerte à J-30)
5. Cliquer sur **Enregistrer**

> Le mandat est créé à l'état **Actif** et apparaît dans la liste des mandats en cours.

### 4.2 Suivre le pipeline de vente

Sur la fiche mandat, la **timeline visuelle** affiche les étapes :

```
Mandat signé → Promotion → Visite → Offre → Négociation → Compromis → Acte notarié → Clôturé
```

Pour chaque étape :
1. Cliquer sur l'étape concernée
2. Saisir la **date effective**
3. Ajouter un **commentaire** (ex: "Offre reçue à 48M, négociation en cours")
4. Joindre un **document** (offre signée, compromis, acte notarié)
5. Cliquer sur **Valider l'étape** pour avancer dans le pipeline

**Durées indicatives** :
- Mandat signé → Promotion : immédiat
- Promotion → Visite : 1 à 30 jours
- Visite → Offre : 7 à 60 jours
- Offre → Négociation : 7 à 60 jours
- Négociation → Compromis : 30 à 90 jours
- Compromis → Acte notarié : 60 à 180 jours

### 4.3 Créer un compromis de vente

1. Sur un mandat à l'étape **Négociation**, bouton **Créer compromis**
2. Sélectionner l'**acquéreur** (tiers de type "Acheteur")
3. Renseigner :
   - **Prix final convenu** (après négociation)
   - **Délai pour signature acte définitif** : nombre de jours (généralement 60 à 90)
   - **Conditions suspensives** : liste des conditions à remplir avant la signature finale (obtention prêt bancaire, permis de construire, etc.)
   - **Pénalités de désistement** : montant ou % en cas d'annulation par l'une des parties
4. Joindre le **document de compromis signé**
5. Cliquer sur **Enregistrer**

> Le statut du mandat passe automatiquement à **Compromis**.

### 4.4 Calcul des commissions

Le système calcule automatiquement la commission selon le type configuré sur le mandat :

| Type de commission | Formule | Exemple avec prix de vente 50M FCFA |
|--------------------|---------|-------------------------------------|
| **Fixe** | Montant forfaitaire | 2 500 000 FCFA |
| **Pourcentage** | % du prix de vente | 5% × 50M = **2 500 000 FCFA** |
| **Échelonnée** | % dégressif par tranche | 5% jusqu'à 50M, 4% au-delà → 2 500 000 FCFA |

La commission peut être **répartie** :
- Commission agence (montant total perçu)
- Sous-commission agent commercial (part reversée à l'agent ayant conclu la vente)

> **Frais et taxes** affichés à titre informatif sur le compromis :
> - Droit d'enregistrement : 6% du prix (acheteur)
> - TVA (construction neuve) : 18% du prix (acheteur)
> - Frais notariés : ~2-3% du prix (acheteur)
> - Commission agence : selon mandat (vendeur)

---

## 5. Rénovation

### 5.1 Créer une fiche de travaux

1. Menu `Immobilier > Rénovation > Nouveau`
2. Sélectionner le **bien** concerné
3. Renseigner :
   - **Libellé** : ex: "Rénovation complète cuisine et salle de bain"
   - **Budget prévisionnel** (ex: 5 000 000 FCFA)
   - **Date de début** prévue
   - **Date de fin prévue**
   - **Description détaillée** : travaux prévus, matériaux, fournisseurs
4. Cliquer sur **Enregistrer**

> La fiche est créée à l'état **Brouillon**.

### 5.2 Suivi des états de travaux

| État | Description | Actions possibles |
|------|-------------|-------------------|
| **Brouillon** | Fiche créée, non validée | Modifier, Supprimer |
| **Validé** | Budget approuvé par le propriétaire | Démarrer les travaux |
| **En cours** | Travaux en activité | Mettre à jour l'avancement, enregistrer des dépenses |
| **Terminé** | Travaux réceptionnés | Saisir le coût réel, comparer au budget |
| **Annulé** | Projet abandonné | Archiver la fiche |

Pour changer d'état :
1. Ouvrir la fiche de travaux
2. Bouton correspondant à l'état souhaité
3. Saisir un commentaire (obligatoire pour "Terminé", recommandé pour les autres)

### 5.3 Suivi budgétaire

Sur la fiche travaux, onglet **Budget** :

| Indicateur | Description |
|------------|-------------|
| **Budget prévu** | Montant estimé lors de la création |
| **Coût réel** | Montant final saisi à la fin des travaux |
| **Écart** | `Coût réel - Budget prévu` |

**Indicateur couleur** :
- **Vert** : dans le budget (Écart ≤ 0)
- **Orange** : dépassement modéré (0 < Écart ≤ 10%)
- **Rouge** : dépassement significatif (Écart > 10%)

> Le suivi budgétaire permet d'évaluer la qualité des estimations et d'affiner les budgets futurs.

---

## 6. Syndic de copropriété

### 6.1 Créer une copropriété

1. Menu `Immobilier > Syndic > Copropriétés > Nouveau**
2. Renseigner :
   - **Nom** de l'immeuble (ex: "Résidence Les Cocotiers")
   - **Adresse** complète
   - **Nombre total de lots** : appartements + commerces + parkings
   - **Total des tantièmes** : généralement 1000 (peut varier selon le règlement de copropriété)
3. Cliquer sur **Enregistrer**

### 6.2 Gérer les lots

Sur la fiche copropriété, onglet **Lots** :

1. Bouton **Nouveau lot**
2. Renseigner :
   - **Référence** : ex: "A-101" (étage + numéro), "RDC-Commerce" (rez-de-chaussée)
   - **Surface** en m²
   - **Tantièmes** : parts de propriété (ex: 120/1000)
   - **Propriétaire** : tiers de type "Propriétaire"
   - **Bien lié** : si le lot est géré par l'agence en location
3. Enregistrer

> **Vérification** : la somme des tantièmes de tous les lots doit être égale au total des tantièmes de la copropriété. Le système affiche un avertissement si ce n'est pas le cas.

### 6.3 Créer une charge de copropriété

1. Fiche copropriété > onglet **Charges**
2. Bouton **Nouvelle charge**
3. Renseigner :
   - **Type** : Générale, Ascenseur, Chauffage, Entretien, Gardiennage, Électricité communes, etc.
   - **Montant total** de la charge (ex: 3 000 000 FCFA)
   - **Période** : mois et année concernés (ex: Mars 2026)
4. Enregistrer

### 6.4 Répartition par tantième

Le système calcule automatiquement la part de chaque lot selon la formule :

```
Part du lot = Montant total × (Tantièmes du lot / Tantièmes total de la copropriété)
```

Sur la fiche charge, le tableau affiche :

| Lot | Tantièmes | Part à payer (FCFA) | Payé (FCFA) | Solde (FCFA) |
|-----|-----------|---------------------|-------------|--------------|
| A-101 | 120 | 360 000 | 360 000 | **0** |
| A-102 | 100 | 300 000 | 150 000 | **150 000** |
| A-103 | 120 | 360 000 | 0 | **360 000** |
| ... | ... | ... | ... | ... |

**Codes couleur des soldes** :
- **Vert** : payé intégralement
- **Orange** : paiement partiel
- **Rouge** : impayé

### 6.5 Appel de fonds et enregistrement des paiements

1. Sur la fiche charge, bouton **Générer appel de fonds**
2. Le système génère un document PDF par lot avec le montant à payer
3. Envoi aux propriétaires (email ou impression)
4. Lorsqu'un paiement est reçu :
   - Fiche charge > ligne du lot > **Enregistrer paiement**
   - Saisir : montant, date, mode (virement, espèces, Djamo)
5. Le solde se met à jour automatiquement

> Le suivi des impayés est visible par lot et par période dans le rapport de synthèse du syndic.

---

## 7. Étude de marché

### 7.1 Saisir une transaction comparable (vente)

1. Menu `Immobilier > Étude de marché > Ventes comparables > Nouveau**
2. Renseigner :
   - **Quartier** : ex: "Cocody Angré", "Marcory Résidentiel"
   - **Ville** : ex: "Abidjan", "Bouaké"
   - **Type de bien** : Maison, Appartement, Bureau...
   - **Surface** en m²
   - **Nombre de pièces**
   - **Prix de transaction** réel (FCFA)
   - **Source** : Notaire, Site web (CoinAfrique, Jumia Deals...), Estimation, Bailleur
3. Cliquer sur **Enregistrer**

> Le **prix au m²** est calculé automatiquement : `Prix de transaction / Surface`

### 7.2 Saisir une location comparable

1. Menu `Immobilier > Étude de marché > Locations comparables > Nouveau**
2. Renseigner :
   - Quartier, ville, type, surface, nombre de pièces
   - **Loyer mensuel** réel
   - **Charges mensuelles** (si connues)
3. Cliquer sur **Enregistrer**

> Le **loyer au m²** est calculé automatiquement : `Loyer mensuel / Surface`

### 7.3 Rechercher les comparables

Menu `Immobilier > Étude de marché > Recherche` :

**Filtres disponibles** :
- Quartier (autocomplétion)
- Type de bien
- Surface minimale et maximale
- Période de transaction

**Résultats** :
- Tableau des transactions correspondantes
- **Prix/m² moyen**, **minimum** et **maximum**
- Graphique d'évolution par trimestre

> **Usage** : Aider l'agent à évaluer le prix de vente ou de location d'un nouveau bien. Consulter les comparables avant de créer un mandat de vente ou un bail.

---

## 8. Paiement mobile Djamo

### 8.1 Prérequis (à configurer par l'administrateur)

Avant d'utiliser Djamo, l'administrateur doit avoir configuré :
- `DJAMO_CLIENT_ID`
- `DJAMO_CLIENT_SECRET`
- `DJAMO_ENV` (sandbox pour tests, production pour réel)

> Si ces paramètres ne sont pas configurés, le bouton "Payer avec Djamo" n'apparaît pas.

### 8.2 Créer une demande de paiement

1. Ouvrir une **quittance impayée**
2. Bouton **Payer avec Djamo**
3. Le système affiche :
   - **Montant** à payer
   - **Numéro de téléphone** du locataire (récupéré depuis sa fiche)
4. Cliquer sur **Générer le lien de paiement**
5. Le système crée :
   - Un **lien de paiement** (URL sécurisée)
   - Un **QR code** (image scannable)
6. Envoyer au locataire :
   - Par **SMS** (si intégration SMS configurée)
   - Par **email**
   - Par **WhatsApp** (manuellement)

### 8.3 Suivre les transactions

Menu `Immobilier > Paiements > Transactions Djamo` :

| Colonne | Description |
|---------|-------------|
| Référence | ID interne (`DJA-YYYY-NNNN`) |
| Quittance liée | Lien vers la quittance concernée |
| Montant | Montant demandé au locataire |
| Téléphone | Numéro du locataire |
| ID transaction Djamo | Identifiant externe chez Djamo |
| Statut | État du paiement |
| Date | Date de création |

**Statuts possibles** :
| Statut | Signification | Action |
|--------|---------------|--------|
| **En attente** | Lien généré, paiement non effectué | Relancer le locataire |
| **Succès** | Paiement confirmé par Djamo | Vérifier l'encaissement sur la quittance |
| **Échec** | Paiement refusé ou expiré | Contacter le locataire, proposer autre mode |
| **Remboursé** | Paiement annulé et remboursé | Vérifier le motif, ajuster la quittance |

### 8.4 Webhook (notification automatique)

Lorsqu'un paiement est confirmé par Djamo, le système reçoit automatiquement une notification (webhook) qui :

1. Met à jour le statut de la transaction : "En attente" → "Succès"
2. Enregistre automatiquement le paiement sur la **quittance** concernée :
   - Montant = montant payé
   - Mode = "Djamo"
   - Date = date de confirmation
3. Recalcule le **solde** du bail (Total dû - Montant payé)
4. Envoie une **confirmation au locataire** par SMS (si configuré)
5. Met à jour l'**échéancier** avec le nouveau statut

> Aucune action manuelle n'est requise de la part de l'agent lorsque le webhook fonctionne correctement.

---

## 9. Rapports et tableaux de bord

### 9.1 Tableau de bord principal

Menu `Immobilier > Rapports > Tableau de bord`

Le tableau de bord affiche des **indicateurs de performance (KPIs)** mis à jour en temps réel.

#### KPIs locatifs

| Indicateur | Formule | Usage |
|------------|---------|-------|
| **Taux d'occupation** | `(Nombre de biens loués / Nombre total de biens) × 100` | Évaluer la saturation du parc |
| **Taux d'encaissement** | `(Montant perçu / Montant attendu sur le mois) × 100` | Mesurer la rentabilité immédiate |
| **Impayés en cours** | Somme des soldes des quittances impayées | Identifier les créances douteuses |
| **Baux expirant** | Baux dont la date de fin est dans moins de 3 mois | Anticiper les renouvellements |

#### KPIs ventes

| Indicateur | Formule | Usage |
|------------|---------|-------|
| **Délai moyen de vente** | Moyenne des jours entre mandat et compromis | Évaluer la vélocité commerciale |
| **Prix moyen au m²** | Moyenne des prix/m² par quartier et type | Positionner les nouveaux biens |
| **Commissions encaissées** | Somme des commissions par agent et par mois | Calculer les rémunérations |
| **Mandats actifs** | Nombre et valeur totale des mandats en cours | Mesurer le portefeuille |

#### KPIs financiers

| Indicateur | Formule | Usage |
|------------|---------|-------|
| **Chiffre d'affaires mensuel** | Loyers perçus + Commissions de vente | Suivi global de l'activité |
| **Charges de syndic** | Total des charges par copropriété et par période | Suivi de la trésorerie syndic |
| **Rentabilité par bien** | `(Loyers perçus annuels / Prix d'acquisition) × 100` | Comparer la performance des investissements |

### 9.2 Créer un rapport personnalisé

1. Menu `Immobilier > Rapports > Configurer`
2. Bouton **Nouveau rapport**
3. Renseigner :
   - **Nom** : ex: "Situation trimestrielle", "Bilan annuel"
   - **Type** :
     - **Trésorerie** : flux entrants et sortants
     - **Occupation** : taux de remplissage et vacance
     - **Commercial** : performances des agents, délais de vente
     - **Impayés** : suivi des créances et relances
   - **Période** : Mensuel, Trimestriel, Annuel
   - **Colonnes** : sélectionner les indicateurs à afficher dans le tableau
   - **Inclure un graphique** : cochez pour ajouter une visualisation
   - **Envoi automatique** : cochez pour recevoir le rapport par email périodiquement
     - Fréquence : hebdomadaire, mensuelle, trimestrielle
     - Destinataires : liste d'emails (séparés par des virgules)
4. Cliquer sur **Enregistrer**

> Le rapport apparaît dans la liste et peut être généré à tout moment.

### 9.3 Exporter et imprimer

Sur chaque rapport (tableau de bord ou rapport personnalisé) :

| Action | Format | Usage |
|--------|--------|-------|
| **Export CSV** | Fichier `.csv` | Traitement dans Excel, analyse externe |
| **Export PDF** | Fichier `.pdf` | Présentation direction, archivage |
| **Imprimer** | Version papier | Réunion, signature |

---

*Guide Utilisateur — Gestion Agence Immobilière Côte d'Ivoire | v1.0 | Mai 2026*
