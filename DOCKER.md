# Docker Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed on your system

## Starting Services

### Start PostgreSQL and Redis:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379

### Check services are running:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs -f
```

## Database Connection

When using Docker PostgreSQL, update your `.env` file or use these connection details:

```
DB_NAME=sports_tracker
DB_USER=sportsuser
DB_PASSWORD=sportspass
DB_HOST=localhost
DB_PORT=5432
```

In `config/settings/development.py`, uncomment the PostgreSQL database configuration.

## Stopping Services

```bash
docker-compose down
```

To also remove volumes (⚠️ this deletes all data):
```bash
docker-compose down -v
```

## Useful Commands

```bash
# Restart services
docker-compose restart

# Stop services without removing containers
docker-compose stop

# View resource usage
docker-compose stats

# Access PostgreSQL shell
docker-compose exec db psql -U sportsuser -d sports_tracker

# Access Redis CLI
docker-compose exec redis redis-cli
```

## Troubleshooting

### Port Already in Use
If ports 5432 or 6379 are already in use, modify the ports in `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"  # Change 5432 to 5433 or another available port
```

### Permission Issues
If you encounter permission issues with volumes:
```bash
docker-compose down -v
docker volume prune
docker-compose up -d
```
