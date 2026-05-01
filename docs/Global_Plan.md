# Plan Global — Gestion Agence Immobilière (Côte d'Ivoire)

## Vue d'ensemble

Cette solution vise à développer un ERP immobilier vertical basé sur **Dolibarr 23.x**, spécifiquement adapté aux agences immobilières en Côte d'Ivoire. Elle couvre l'ensemble du cycle de vie d'un bien immobilier : acquisition, rénovation, mise en location ou vente, gestion locative, syndic de copropriété, et analyse de marché.

L'architecture repose sur une **approche modulaire configurable** : chaque module peut être activé ou désactivé selon les besoins de l'agence.

## Objectifs stratégiques

1. **Centralisation** : Un seul outil pour gérer biens, clients, baux, ventes, travaux et syndic.
2. **Conformité locale** : Respect des obligations fiscales ivoiriennes (TLPPU, frais d'enregistrement, TVA).
3. **Paiement mobile** : Intégration native de **Djamo** pour l'encaissement des loyers.
4. **Évolutivité** : Architecture préparée pour l'intégration future du cadastre numérique DGFLTI.
5. **Accessibilité** : Interface web responsive, utilisable sur desktop et tablette (pas d'application mobile native).

## Architecture logicielle

```
┌─────────────────────────────────────────────────────────────────┐
│                   Dolibarr 23.x (Docker)                        │
│                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ mod_immo_   │ │ mod_immo_   │ │ mod_immo_   │   [MVP]       │
│  │   bien      │ │   client    │ │   locatif   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ mod_immo_   │ │ mod_immo_   │ │ mod_immo_   │  [Phase 2]    │
│  │   vente     │ │   reno      │ │   syndic    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ mod_immo_   │ │ mod_immo_   │ │ mod_immo_   │  [Phase 3]    │
│  │   marche    │ │   djamo     │ │   rapports  │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              mod_immo_core (base commune)               │    │
│  │  • Configuration modules (activation/désactivation)     │    │
│  │  • Système de droits et rôles                           │    │
│  │  • Hooks cadastre (DGFLTI)                              │    │
│  │  • Tables pivot communes                                │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │ PostgreSQL 15 │    │  API Djamo   │
            │   (Docker)   │    │   (REST)     │
            └──────────────┘    └──────────────┘
```

## Stack technique

| Couche | Technologie |
|--------|-------------|
| ERP | Dolibarr 23.x (PHP 8.4) |
| Base de données | PostgreSQL 15 |
| Conteneurisation | Docker + Docker Compose |
| Frontend | Dolibarr native + thème responsive possible |
| Paiement | API REST Djamo |
| Tests | PHPUnit 11, scripts PHP custom |
| Documentation | Markdown (ce dépôt) |

## Modules Dolibarr (9 modules + core)

### Core — mod_immo_core
Base commune à tous les modules immobiliers. Gère la configuration, l'activation des modules, le système de droits, et les hooks d'intégration cadastre.

### MVP — Phase 1

| Module | Numéro | Description |
|--------|--------|-------------|
| `mod_immo_bien` | 700001 | Gestion des biens immobiliers : fiche, typologie, photos, documents, géolocalisation, états |
| `mod_immo_client` | 700002 | CRM immobilier : tiers (propriétaire, locataire, acheteur, prospect), contacts, visites |
| `mod_immo_locatif` | 700003 | Gestion locative : baux, quittances, échéancier, indexation loyer, TLPPU automatique |

### Phase 2

| Module | Numéro | Description |
|--------|--------|-------------|
| `mod_immo_vente` | 700004 | Transactions de vente : mandats, compromis, actes notariés, commissions |
| `mod_immo_reno` | 700005 | Suivi des travaux de rénovation : devis, budget, avancement, changement d'état |
| `mod_immo_syndic` | 700006 | Syndic de copropriété : charges communes, appels de fonds, assemblées générales |

### Phase 3

| Module | Numéro | Description |
|--------|--------|-------------|
| `mod_immo_marche` | 700007 | Étude de marché : saisie prix/m², évolution, comparables, export PDF |
| `mod_immo_djamo` | 700008 | Intégration Djamo : paiement loyers, QR code, suivi transactions |
| `mod_immo_rapports` | 700009 | Tableaux de bord : KPIs, taux d'occupation, rentabilité, impayés |

## Spécificités légales et fiscales — Côte d'Ivoire

| Aspect | Détail | Module impacté |
|--------|--------|----------------|
| **TLPPU (Taxe Locale sur la Propriété et la Publicité)** | 11% à 20% du loyer annuel net selon la commune | `mod_immo_locatif` |
| **Frais d'enregistrement bail** | 6% pour baux > 1 an | `mod_immo_locatif` |
| **Caution / Avance** | 1 à 3 mois de loyer selon convention | `mod_immo_locatif` |
| **TVA vente** | 18% sur constructions nouvelles | `mod_immo_vente` |
| **Commission agence** | Variable (5-10% vente, 1-2 mois location) | `mod_immo_vente`, `mod_immo_locatif` |
| **Cadastre** | Déploiement progressif DGFLTI | `mod_immo_core` (hooks futurs) |
| **Paiement mobile** | Djamo, Orange Money, MTN Mobile Money | `mod_immo_djamo` |

## Plan de développement (Roadmap)

### Phase 1 — MVP (Sprint 1-6)

**Objectif** : Livrer les 3 modules core pour une gestion locative fonctionnelle.

| Sprint | Livrable |
|--------|----------|
| 1-2 | `mod_immo_core` : architecture, activation modules, droits, configuration |
| 3-4 | `mod_immo_bien` : fiche bien, typologie, photos, documents |
| 5-6 | `mod_immo_client` + `mod_immo_locatif` : CRM, baux, quittances, TLPPU |

### Phase 2 — Extension (Sprint 7-12)

**Objectif** : Ajouter la vente, la rénovation et le syndic.

| Sprint | Livrable |
|--------|----------|
| 7-8 | `mod_immo_vente` : mandats, compromis, commissions |
| 9-10 | `mod_immo_reno` : suivi travaux, budget, changement d'état |
| 11-12 | `mod_immo_syndic` : charges, appels de fonds, AG |

### Phase 3 — Intégrations (Sprint 13-18)

**Objectif** : Paiement mobile, étude de marché et tableaux de bord.

| Sprint | Livrable |
|--------|----------|
| 13-14 | `mod_immo_djamo` : intégration API, QR code, webhooks |
| 15-16 | `mod_immo_marche` : saisie prix/m², graphiques, comparables |
| 17-18 | `mod_immo_rapports` : dashboard, KPIs, exports CSV/PDF |

## Plan d'enquête — Validation Running Lean

### Phase 1 : Exploration qualitative (Semaine 1-2)
- **Cible** : 5 à 8 agences immobilières
- **Méthode** : Entretiens semi-directifs de 30 minutes
- **Objectif** : Identifier les 3 problèmes les plus critiques

### Phase 2 : Quantification (Semaine 3-4)
- **Cible** : 20 à 30 agences via questionnaire en ligne
- **Méthode** : Google Forms / Enquête terrain
- **Objectif** : Valider l'importance relative des modules proposés

### Phase 3 : Prototype (Semaine 5-6)
- **Cible** : 2 à 3 agences pilotes
- **Méthode** : Tests utilisateurs sur wireframes des modules MVP
- **Objectif** : Affiner l'ergonomie et le périmètre fonctionnel

### Phase 4 : Validation (Semaine 7)
- **Méthode** : Atelier de synthèse avec les agences pilotes
- **Livrable** : Backlog priorisé pour le développement

## Structure des repositories

```
gestion_agence_immo/
├── docs/
│   ├── Global_Plan.md              # Ce fichier
│   ├── mod_immo_core.md
│   ├── mod_immo_bien.md
│   ├── mod_immo_client.md
│   ├── mod_immo_locatif.md
│   ├── mod_immo_vente.md
│   ├── mod_immo_reno.md
│   ├── mod_immo_syndic.md
│   ├── mod_immo_marche.md
│   ├── mod_immo_djamo.md
│   ├── mod_immo_rapports.md
│   ├── Questionnaire_Agence.docx   # Questionnaire terrain
│   └── Presentation_Etude.md       # Présentation introduction étude
├── docker/                         # Configuration Docker
├── htdocs/custom/                  # Modules Dolibarr
│   ├── immocore/
│   ├── immobien/
│   ├── immoclient/
│   ├── immolocatif/
│   ├── immovente/
│   ├── immoreno/
│   ├── immosyndic/
│   ├── immomarche/
│   ├── immodjamo/
│   └── immorapports/
├── tests/                          # Tests PHPUnit
└── README.md
```

## Prochaines étapes

1. [ ] Valider le questionnaire Lean Canvas auprès des agences immobilières
2. [ ] Réaliser les entretiens d'exploration (Phase 1)
3. [ ] Finaliser le backlog MVP à partir des retours terrain
4. [ ] Débuter le développement `mod_immo_core`
5. [ ] Préparer l'environnement Docker (Dolibarr 23.x + PostgreSQL 15)
6. [ ] Créer la structure de base des modules Dolibarr

---

*Projet Gestion Agence Immobilière — Côte d'Ivoire | Plan Global v1.0*
