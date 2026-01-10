# Implementation Plan: Local Development Infrastructure

## Track Overview
- **Track ID:** local_dev_infrastructure_20260110
- **Description:** Docker Compose v2 setup for local development with all TSS PPM services
- **Estimated Phases:** 4

---

## Phase 1: Docker Compose Foundation & Database

### Objective
Create the Docker Compose configuration with PostgreSQL and establish the database schema.

### Tasks

- [~] Task: Create docker-compose.yml with base structure
  - Docker Compose v2 syntax
  - Define internal network `tss-ppm-network`
  - Add PostgreSQL 17 service with health check
  - Configure persistent volume for database data

- [ ] Task: Create database initialization scripts
  - Create `database/init/` directory structure
  - Create `001_schema.sql` with all table definitions
  - Tables: users, reviews, goals, competencies, scores, audit_log
  - Proper foreign keys and indexes

- [ ] Task: Verify PostgreSQL service starts correctly
  - Run `docker compose up db`
  - Confirm health check passes
  - Verify schema is created via psql

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Docker Compose Foundation & Database' (Protocol in workflow.md)

---

## Phase 2: Keycloak Authentication Service

### Objective
Configure Keycloak with the TSS-PPM realm, test users, and custom theme.

### Tasks

- [ ] Task: Add Keycloak service to docker-compose.yml
  - Keycloak 26 image with dev mode
  - Health check configuration
  - Depends on PostgreSQL (optional, can use embedded H2)
  - Mount realm import directory

- [ ] Task: Create Keycloak realm configuration
  - Create `keycloak/tss-ppm-realm.json`
  - Define `tss-ppm` realm settings
  - Configure `tss-ppm-web` client (public, PKCE)
  - Configure `tss-ppm-api` client (bearer-only)
  - Set up role mappings: employee, manager, hr, admin

- [ ] Task: Create test users in realm configuration
  - employee@test.local (employee role)
  - manager@test.local (manager role)
  - hr@test.local (hr role)
  - admin@test.local (admin role)
  - All with password: `test123`

- [ ] Task: Set up custom TSS-PPM login theme
  - Create `keycloak/themes/tss-ppm/` directory
  - Add login theme with brand colors (Magenta/Navy)
  - Configure realm to use custom theme

- [ ] Task: Verify Keycloak service and authentication
  - Run `docker compose up db keycloak`
  - Access admin console at localhost:8080
  - Verify realm imported correctly
  - Test login with test user credentials

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Keycloak Authentication Service' (Protocol in workflow.md)

---

## Phase 3: Application Services

### Objective
Add backend, frontend, and voice services to the Docker Compose configuration.

### Tasks

- [ ] Task: Create backend Dockerfile for development
  - Create/update `backend/Dockerfile`
  - Python 3.11 base image
  - Install dependencies from requirements.txt
  - Configure uvicorn with hot reload

- [ ] Task: Add backend service to docker-compose.yml
  - Build from backend Dockerfile
  - Volume mount for hot reload
  - Environment variables from .env
  - Health check on /health endpoint
  - Depends on db and keycloak health

- [ ] Task: Create frontend development Dockerfile
  - Create `frontend/Dockerfile.dev`
  - Node.js base image
  - Install dependencies
  - Run Vite dev server with host binding

- [ ] Task: Add frontend service to docker-compose.yml
  - Build from frontend Dockerfile.dev
  - Volume mounts for source code (hot reload)
  - Environment variables for API URL and Keycloak
  - Depends on backend health

- [ ] Task: Add voice service to docker-compose.yml
  - faster-whisper-server:latest-cpu image
  - Configure whisper-small model
  - Health check configuration
  - Accessible on port 8001

- [ ] Task: Verify all application services start
  - Run `docker compose up`
  - Confirm all 5 services healthy
  - Check logs for errors

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Application Services' (Protocol in workflow.md)

---

## Phase 4: Integration & Developer Experience

### Objective
Complete the setup with environment configuration, add health endpoint to backend, and verify full stack functionality.

### Tasks

- [ ] Task: Add health check endpoint to backend
  - Create GET /health endpoint in FastAPI
  - Return service status and database connectivity
  - Used by Docker health check

- [ ] Task: Update .env.example with all variables
  - Database configuration
  - Keycloak URLs and client IDs
  - Voice service URL
  - CORS origins for local development

- [ ] Task: Create .env from .env.example with dev defaults
  - Copy and configure for local development
  - Add to .gitignore if not present

- [ ] Task: Test complete authentication flow
  - Start full stack with `docker compose up`
  - Access frontend at localhost:5173
  - Login with test user via Keycloak
  - Verify JWT token passed to backend

- [ ] Task: Test voice service integration
  - Verify voice endpoint responds
  - Test transcription with sample audio (manual)

- [ ] Task: Document local development setup
  - Update README.md with setup instructions
  - Document test user credentials
  - List all service URLs and ports
  - Troubleshooting common issues

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration & Developer Experience' (Protocol in workflow.md)

---

## Completion Checklist

- [ ] docker-compose.yml created with all 5 services
- [ ] Database schema initialization working
- [ ] Keycloak realm with test users configured
- [ ] Custom login theme applied
- [ ] Backend hot reload functional
- [ ] Frontend hot reload functional
- [ ] Voice service responding
- [ ] Full authentication flow working
- [ ] Documentation complete
