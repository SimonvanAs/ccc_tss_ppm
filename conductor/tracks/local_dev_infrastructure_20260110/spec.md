# Specification: Local Development Infrastructure

## Overview

Set up a complete local development environment using Docker Compose v2 that enables developers to run the full TSS PPM stack with a single command. This infrastructure track provides the foundation for manual testing and development of all application features.

## Track Type

Chore / Infrastructure

## Functional Requirements

### FR1: Docker Compose Configuration
- Create `docker-compose.yml` using Docker Compose v2 syntax
- Single `docker compose up` command starts all services
- Health checks ensure proper startup order (database → keycloak → backend → frontend)
- All services connected via internal Docker network

### FR2: PostgreSQL 17 Service
- PostgreSQL 17 Alpine image
- Persistent volume for data storage
- Database initialization via SQL scripts in `database/init/`
- Schema-only initialization (no seed data)
- Accessible on port 5432

### FR3: Keycloak 26 Service
- Keycloak 26 image with development mode enabled
- Pre-configured `tss-ppm` realm via realm JSON import
- Test users for each role: employee, manager, HR, admin
- Custom TSS-PPM login theme installed
- Clients configured: `tss-ppm-web` (public), `tss-ppm-api` (bearer-only)
- Accessible on port 8080

### FR4: Backend Service (FastAPI)
- Build from `backend/Dockerfile`
- Hot reload enabled for development
- Depends on PostgreSQL and Keycloak health
- Environment variables from `.env` file
- Accessible on port 8000

### FR5: Frontend Service (Vite)
- Build from `frontend/Dockerfile.dev` (development mode)
- Hot reload enabled with volume mounts
- Depends on backend availability
- Accessible on port 5173

### FR6: Voice Service (faster-whisper)
- faster-whisper-server CPU image
- Whisper small model for EN/NL/ES transcription
- Accessible on port 8001

### FR7: Environment Configuration
- `.env.example` updated with all required variables
- `.env` file used by docker compose for configuration
- Sensible development defaults (non-production passwords acceptable)

## Non-Functional Requirements

### NFR1: Startup Time
- Full stack should be ready within 60 seconds on a modern machine (excluding first-time image pulls)

### NFR2: Resource Usage
- Reasonable memory footprint for development machines (target: <4GB total)

### NFR3: Developer Experience
- Clear console output showing service status
- Graceful shutdown with `docker compose down`
- Volume persistence for database between restarts

## Acceptance Criteria

1. Running `docker compose up` starts all 5 services successfully
2. Frontend accessible at http://localhost:5173
3. Backend API accessible at http://localhost:8000/docs (Swagger UI)
4. Keycloak admin console accessible at http://localhost:8080
5. Can log in to frontend using test user credentials
6. Voice transcription endpoint responds at http://localhost:8001
7. Database schema is created automatically on first startup
8. Hot reload works for both frontend and backend code changes

## Out of Scope

- Production deployment configuration (Caddy, TLS, etc.)
- Seed data / sample reviews (schema only)
- CI/CD pipeline configuration
- GPU-accelerated voice service
- Database backup/restore procedures
