# TSS PPM v3.0 - Production Deployment Guide

This guide covers deploying TSS PPM to a production environment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Configuration](#configuration)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Database Setup](#database-setup)
- [Keycloak Configuration](#keycloak-configuration)
- [Environment Variables](#environment-variables)
- [Health Checks](#health-checks)
- [Backup and Recovery](#backup-and-recovery)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security Checklist](#security-checklist)

---

## Prerequisites

### Server Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 20 GB SSD | 50 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |

### Software Requirements

- Docker Engine 24.0+
- Docker Compose v2.20+
- Git

### Network Requirements

- Domain name (e.g., `ppm.yourcompany.com`)
- Ports 80 and 443 open for HTTP/HTTPS
- Outbound internet access (for Docker images and Let's Encrypt)

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd ccc_tss_ppm

# 2. Create production environment file
cp .env.example .env.production
nano .env.production  # Edit with production values

# 3. Update Caddyfile with your domain
nano Caddyfile  # Replace ppm.tss-vms.co.uk with your domain

# 4. Start services with production profile
docker compose --env-file .env.production --profile production up -d

# 5. Verify all services are running
docker compose ps
```

---

## Architecture Overview

```
                     Internet
                        │
                        ▼
              ┌─────────────────┐
              │  Caddy (TLS)    │ :443, :80
              │  Reverse Proxy  │
              └────────┬────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Frontend   │ │    API      │ │  Keycloak   │
│  (Vue SPA)  │ │  (FastAPI)  │ │   (Auth)    │
│    :80      │ │   :8000     │ │   :8080     │
└─────────────┘ └──────┬──────┘ └─────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │   Whisper   │ │ WeasyPrint  │
│  (Database) │ │   (Voice)   │ │   (PDF)     │
│   :5432     │ │   :8001     │ │ (in API)    │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Services

| Service | Image | Purpose |
|---------|-------|---------|
| `caddy` | `caddy:2-alpine` | TLS termination, reverse proxy |
| `frontend` | Custom build | Vue 3 SPA |
| `api` | Custom build | FastAPI backend |
| `keycloak` | `quay.io/keycloak/keycloak:26.0` | Authentication (OIDC) |
| `postgres` | `postgres:17-alpine` | Primary database |
| `whisper` | `fedirz/faster-whisper-server:latest-cpu` | Voice transcription |

---

## Configuration

### 1. Environment File (`.env.production`)

Create a production environment file:

```bash
# =============================================================================
# DATABASE
# =============================================================================
DB_USER=ppm
DB_PASSWORD=<STRONG_PASSWORD_HERE>
DB_NAME=tss_ppm

# =============================================================================
# KEYCLOAK
# =============================================================================
KC_ADMIN=admin
KC_ADMIN_PASSWORD=<STRONG_ADMIN_PASSWORD_HERE>

# =============================================================================
# API
# =============================================================================
LOG_LEVEL=WARNING
CORS_ORIGINS=https://ppm.yourcompany.com

# =============================================================================
# FRONTEND
# =============================================================================
VITE_API_URL=https://ppm.yourcompany.com/api/v1
VITE_KEYCLOAK_URL=https://ppm.yourcompany.com/auth
VITE_KEYCLOAK_REALM=tss-ppm
VITE_KEYCLOAK_CLIENT_ID=tss-ppm-web
```

### 2. Caddyfile

Update the domain in `Caddyfile`:

```caddyfile
{
    email admin@yourcompany.com
}

ppm.yourcompany.com {
    # Keycloak authentication
    handle /auth/* {
        reverse_proxy keycloak:8080
    }

    # API backend
    handle /api/* {
        reverse_proxy api:8000
    }

    # Frontend SPA (default)
    handle {
        reverse_proxy frontend:80
    }

    # Security headers
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
    }
}
```

---

## Step-by-Step Deployment

### Step 1: Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Logout and login to apply docker group
```

### Step 2: Clone and Configure

```bash
# Clone repository
git clone <repository-url> /opt/tss-ppm
cd /opt/tss-ppm

# Create environment file
cp .env.example .env.production

# Generate secure passwords
echo "DB_PASSWORD=$(openssl rand -base64 32)" >> .env.production
echo "KC_ADMIN_PASSWORD=$(openssl rand -base64 32)" >> .env.production

# Edit remaining configuration
nano .env.production
```

### Step 3: Configure Domain

```bash
# Update Caddyfile with your domain
sed -i 's/ppm.tss-vms.co.uk/ppm.yourcompany.com/g' Caddyfile

# Update email for Let's Encrypt
sed -i 's/admin@tss.eu/admin@yourcompany.com/g' Caddyfile
```

### Step 4: Build and Start Services

```bash
# Build custom images
docker compose build

# Start all services with production profile
docker compose --env-file .env.production --profile production up -d

# Watch logs during startup
docker compose logs -f
```

### Step 5: Verify Deployment

```bash
# Check all services are running
docker compose ps

# Test health endpoints
curl -k https://ppm.yourcompany.com/api/v1/health
curl -k https://ppm.yourcompany.com/auth/health

# Check Keycloak admin console
# Navigate to: https://ppm.yourcompany.com/auth/admin
```

---

## SSL/TLS Configuration

Caddy automatically obtains and renews Let's Encrypt certificates. Requirements:

1. **DNS**: Your domain must point to the server's IP address
2. **Ports**: Ports 80 and 443 must be accessible from the internet
3. **Email**: Valid email in Caddyfile for Let's Encrypt notifications

### Using Custom Certificates

If you have your own certificates:

```caddyfile
ppm.yourcompany.com {
    tls /etc/caddy/certs/cert.pem /etc/caddy/certs/key.pem

    # ... rest of config
}
```

Mount certificates in docker-compose:

```yaml
caddy:
  volumes:
    - ./certs:/etc/caddy/certs:ro
```

---

## Database Setup

### Initial Setup

The database schema is automatically applied on first startup via the init scripts in `database/init/`.

### Manual Migration

```bash
# Connect to database
docker exec -it tss_ppm_db psql -U ppm -d tss_ppm

# Run a specific migration
docker exec -i tss_ppm_db psql -U ppm -d tss_ppm < database/init/002_seed_data.sql
```

### Database Backup

```bash
# Create backup
docker exec tss_ppm_db pg_dump -U ppm tss_ppm > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated daily backup (add to crontab)
0 2 * * * docker exec tss_ppm_db pg_dump -U ppm tss_ppm | gzip > /backups/tss_ppm_$(date +\%Y\%m\%d).sql.gz
```

### Database Restore

```bash
# Stop API to prevent connections
docker compose stop api

# Restore from backup
docker exec -i tss_ppm_db psql -U ppm -d tss_ppm < backup.sql

# Restart API
docker compose start api
```

---

## Keycloak Configuration

### Realm Configuration

The realm is auto-imported from `keycloak/tss-ppm-realm.json` on first startup.

### Post-Deployment Tasks

1. **Change admin password**:
   - Login to `https://ppm.yourcompany.com/auth/admin`
   - Go to Users → admin → Credentials → Reset Password

2. **Configure EntraID/Azure AD Federation** (if using):
   - Go to Identity Providers → Add Provider → OpenID Connect
   - Configure with your Azure AD tenant details

3. **Update Keycloak URLs** (if domain differs from localhost):
   ```bash
   # Access Keycloak admin
   docker exec -it tss_ppm_auth /opt/keycloak/bin/kcadm.sh config credentials \
     --server http://localhost:8080 --realm master --user admin --password <password>

   # Update realm settings
   docker exec -it tss_ppm_auth /opt/keycloak/bin/kcadm.sh update realms/tss-ppm \
     -s "attributes.frontendUrl=https://ppm.yourcompany.com/auth"
   ```

### Create Production Users

```bash
# Access Keycloak admin console
# https://ppm.yourcompany.com/auth/admin

# 1. Go to Users → Add User
# 2. Set username, email, first/last name
# 3. Go to Credentials tab → Set password (disable temporary)
# 4. Go to Role Mappings → Assign roles (employee, manager, hr, admin)
# 5. Go to Attributes → Add opco_id attribute
```

---

## Environment Variables

### API Service

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `KEYCLOAK_URL` | Internal Keycloak URL | `http://keycloak:8080` |
| `KEYCLOAK_REALM` | Keycloak realm name | `tss-ppm` |
| `KEYCLOAK_CLIENT_ID` | API client ID | `tss-ppm-api` |
| `KEYCLOAK_ISSUER_URL` | Public Keycloak URL | Required for token validation |
| `WHISPER_SERVICE_URL` | Voice service URL | `http://whisper:8000` |
| `CORS_ORIGINS` | Allowed CORS origins | Required |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend Service

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Public API URL | Required |
| `VITE_KEYCLOAK_URL` | Public Keycloak URL | Required |
| `VITE_KEYCLOAK_REALM` | Keycloak realm | `tss-ppm` |
| `VITE_KEYCLOAK_CLIENT_ID` | Frontend client ID | `tss-ppm-web` |

---

## Health Checks

### Endpoints

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| API | `/api/v1/health` | `{"status": "healthy"}` |
| Keycloak | `/auth/health` | `{"status": "UP"}` |
| PostgreSQL | Via Docker healthcheck | Exit code 0 |

### Monitoring Commands

```bash
# Check all container health status
docker compose ps

# Check specific service logs
docker compose logs -f api --tail 100

# Check database connections
docker exec tss_ppm_db psql -U ppm -d tss_ppm -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Backup and Recovery

### Automated Backup Script

Create `/opt/tss-ppm/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/tss-ppm"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker exec tss_ppm_db pg_dump -U ppm tss_ppm | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /opt/tss-ppm/backup.sh >> /var/log/tss-ppm-backup.log 2>&1
```

### Disaster Recovery

```bash
# 1. Stop all services
docker compose down

# 2. Restore database
gunzip -c /backups/tss-ppm/db_YYYYMMDD_HHMMSS.sql.gz | docker exec -i tss_ppm_db psql -U ppm -d tss_ppm

# 3. Start services
docker compose --env-file .env.production --profile production up -d
```

---

## Monitoring

### Log Aggregation

All services output JSON-formatted logs to stdout. Collect with your preferred solution:

```bash
# View real-time logs
docker compose logs -f

# Export logs to file
docker compose logs --no-color > logs_$(date +%Y%m%d).txt
```

### Resource Monitoring

```bash
# Container resource usage
docker stats

# Disk usage
docker system df
```

### Recommended Monitoring Stack

For production monitoring, consider adding:

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and alerting
- **Loki**: Log aggregation

---

## Troubleshooting

### Common Issues

#### 1. Keycloak Won't Start

```bash
# Check logs
docker compose logs keycloak

# Common causes:
# - Database not ready (wait for postgres healthcheck)
# - Invalid realm JSON (check import file)
# - Port conflict (check port 8080)
```

#### 2. API Can't Connect to Database

```bash
# Check database is running
docker compose ps postgres

# Test connection manually
docker exec -it tss_ppm_api python -c "import asyncpg; print('OK')"

# Check DATABASE_URL format
# Should be: postgresql://user:password@postgres:5432/dbname
```

#### 3. Frontend Shows "Unauthorized"

```bash
# Check Keycloak client configuration
# 1. Access Keycloak admin
# 2. Go to Clients → tss-ppm-web
# 3. Verify Valid Redirect URIs includes your domain
# 4. Verify Web Origins includes your domain
```

#### 4. SSL Certificate Issues

```bash
# Check Caddy logs
docker compose logs caddy

# Force certificate renewal
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

#### 5. Voice Service Not Working

```bash
# Check whisper service
docker compose logs whisper

# Test transcription endpoint
curl -X POST http://localhost:8001/v1/audio/transcriptions \
  -F "file=@test.wav" \
  -F "language=en"
```

### Restart Services

```bash
# Restart single service
docker compose restart api

# Restart all services
docker compose --env-file .env.production --profile production restart

# Full rebuild and restart
docker compose down
docker compose build --no-cache
docker compose --env-file .env.production --profile production up -d
```

---

## Security Checklist

Before going live, verify:

- [ ] **Passwords**: All default passwords changed
- [ ] **Environment**: `.env.production` not committed to git
- [ ] **HTTPS**: TLS certificates valid and auto-renewing
- [ ] **Keycloak**: Admin password changed, brute force protection enabled
- [ ] **Database**: Not exposed to public internet (only internal network)
- [ ] **Firewall**: Only ports 80, 443 open externally
- [ ] **Backups**: Automated backup configured and tested
- [ ] **Updates**: Plan for regular security updates
- [ ] **Monitoring**: Health checks and alerting configured
- [ ] **Audit Logs**: Database audit logging enabled

### Security Headers (via Caddy)

The Caddyfile includes these security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000`

---

## Updating the Application

```bash
# 1. Pull latest changes
cd /opt/tss-ppm
git pull origin main

# 2. Rebuild images
docker compose build

# 3. Apply database migrations (if any)
docker exec -i tss_ppm_db psql -U ppm -d tss_ppm < database/migrations/XXX_migration.sql

# 4. Restart services with zero downtime
docker compose --env-file .env.production --profile production up -d --no-deps api frontend

# 5. Verify deployment
curl https://ppm.yourcompany.com/api/v1/health
```

---

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs: `docker compose logs -f`
- Contact: admin@tss.eu
