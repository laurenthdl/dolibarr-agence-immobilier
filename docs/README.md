# Documentation — Gestion Agence Immobilière Côte d'Ivoire

Cette documentation est organisée en trois documents distincts, chacun destiné à un public spécifique.

##  Guide Utilisateur

**Fichier** : `Guide_Utilisateur.md` (640 lignes)

**Public cible** : Agents commerciaux, Gestionnaires locatifs, Comptables, Directeurs d'agence

**Contenu** :
- Biens immobiliers (création, cycle de vie)
- Clients et CRM (tiers, visites)
- Gestion locative (baux, quittances, TLPPU, échéancier, indexation)
- Transactions de vente (mandats, pipeline, compromis, commissions)
- Rénovation (fiches de travaux, suivi budgétaire)
- Syndic de copropriété (copropriétés, lots, charges, répartition par tantième)
- Étude de marché (comparables vente/location)
- Paiement mobile Djamo (création demande, webhook, suivi)
- Rapports et tableaux de bord (KPIs, rapports personnalisés, exports)

##  Guide Administrateur

**Fichier** : `Guide_Administrateur.md` (478 lignes)

**Public cible** : Administrateurs système, Responsables informatiques, Intégrateurs Dolibarr

**Contenu** :
- Vue d'ensemble du projet et architecture
- Prérequis système (serveur, Docker, accès)
- Installation (Docker recommandé + manuelle)
- Configuration initiale (paramètres globaux, activation modules)
- Catalogue de référence (types de bien, états, baux, clients, paiements)
- Gestion des droits utilisateurs (profils prédéfinis, permissions)
- Maintenance et mise à jour (logs, diagnostic)

##  Référence Technique

**Fichier** : `Reference_Technique.md` (837 lignes)

**Public cible** : Ingénieurs système, Développeurs, Intégrateurs avancés

**Contenu** :
- Architecture et modules (table des 10 modules, dépendances, Docker)
- Schéma de données (tables principales, catalogues, historique)
- Numérotation et référencement automatique
- Spécificités fiscales Côte d'Ivoire (TLPPU, TVA, commissions)
- API REST (endpoints prévisionnels, format des réponses)
- **Sauvegarde et restauration** (stratégie, scripts cron, test de restauration)
- **Migration** (Dolibarr, PostgreSQL, rollback)
- **Troubleshooting** (tableau des problèmes courants, diagnostic avancé)
- **Monitoring** (health checks, alertes, métriques Docker, PostgreSQL, CI/CD)
- Support et ressources (URLs, glossaire technique)

## Autres documents

| Fichier | Description |
|---------|-------------|
| `Global_Plan.md` | Plan global du projet, stack technique, roadmap |
| `mod_immo_*.md` | Spécifications détaillées par module (10 fichiers) |
| `Presentation_Etude.md` | Présentation de l'étude de marché initiale |
| `Questionnaire_Agence.docx` | Questionnaire terrain pour les agences pilotes |

---

*Documentation v1.0 | Mai 2026*
