# Gestion Agence Immobiliere — Cote d'Ivoire

Suite de 10 modules Dolibarr 23.x pour la gestion immobiliere en Cote d'Ivoire.

## Modules

| # | Module | Numero | Phase | Description |
|---|--------|--------|-------|-------------|
| 1 | **immocore** | 700000 | Core | Configuration globale, activation modules |
| 2 | **immobien** | 700001 | MVP | Gestion des biens (CRUD complet) |
| 3 | **immoclient** | 700002 | MVP | CRM immobilier (tiers + visites) |
| 4 | **immolocatif** | 700003 | MVP | Baux + Quittances + TLPPU auto |
| 5 | **immovente** | 700004 | MVP | Mandats de vente + commissions |
| 6 | **immoreno** | 700005 | Phase 2 | Suivi travaux de renovation |
| 7 | **immosyndic** | 700006 | Phase 2 | Syndic de copropriete |
| 8 | **immomarche** | 700007 | Phase 3 | Etude de marche (prix/m2) |
| 9 | **immodjamo** | 700008 | Phase 3 | Paiement mobile (Djamo) |
| 10 | **immorapports** | 700009 | Phase 4 | Dashboard + KPIs |

## Installation rapide

```bash
git clone https://github.com/laurenthdl/dolibarr-agence-immobilier.git
cd dolibarr-agence-immobilier
./install.sh
```

## Documentation

- [Guide Utilisateur](docs/Guide_Utilisateur.md) — Procedures operationnelles
- [Guide Administrateur](docs/Guide_Administrateur.md) — Installation et configuration
- [Reference Technique](docs/Reference_Technique.md) — Architecture, SQL, API, monitoring

## Scripts d'administration

| Script | Description |
|--------|-------------|
| `install.sh` | Installation automatisée (Docker + modules + SQL) |
| `scripts/backup.sh` | Sauvegarde PostgreSQL + documents |
| `scripts/healthcheck.sh` | Verification sante des services |
| `scripts/restore.sh` | Restauration depuis un backup |
| `scripts/update.sh` | Mise a jour des modules depuis Git |

## Stack

- Dolibarr 23.x (PHP 8.1+)
- PostgreSQL 15
- Docker + Docker Compose
- PHPUnit 11

## License

GPLv3
