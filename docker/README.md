# Commandes Docker pour le projet Immobilier

## Démarrer l'environnement
```bash
docker-compose up -d
```

## Accès
- Dolibarr: http://localhost:8080 (admin/admin)
- pgAdmin: http://localhost:8081 (admin@localhost.com/admin)
- PostgreSQL: localhost:5432

## Modules custom montés
Tous les modules sont montés en lecture seule dans `/var/www/html/custom/` :
- `immocore`, `immobien`, `immoclient`, `immolocatif`, `immovente`

## Commandes utiles

```bash
# Voir les logs
docker-compose logs -f dolibarr

# Mettre à jour un module sans redémarrer
docker-compose restart dolibarr

# Shell dans le conteneur Dolibarr
docker-compose exec dolibarr bash

# Activer un module en CLI
docker-compose exec -u www-data dolibarr php /var/www/html/bin/activate-modules.php immocore

# Backup base de données
docker-compose exec db pg_dump -U dolibarr dolibarr > backup.sql
```
