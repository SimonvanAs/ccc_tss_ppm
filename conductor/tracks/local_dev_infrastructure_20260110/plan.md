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

- [x] Task: Create docker-compose.yml with base structure (existing)
  - Docker Compose v2 syntax
  - Define internal network `tss-ppm-network`
  - Add PostgreSQL 17 service with health check
  - Configure persistent volume for database data

- [x] Task: Create database initialization scripts (existing)
  - Create `database/init/` directory structure
  - Create `01-schema.sql` with all table definitions
  - Tables: users, reviews, goals, competencies, scores, audit_log
  - Proper foreign keys and indexes

- [x] Task: Verify PostgreSQL service starts correctly (6018a71)
  - Run `docker compose up postgres`
  - Confirm health check passes
  - Verify schema is created via psql

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Docker Compose Foundation & Database' (Protocol in workflow.md)

---

## Phase 2: Keycloak Authentication Service

### Objective
Configure Keycloak with the TSS-PPM realm, test users, and custom theme.

### Tasks

- [x] Task: Add Keycloak service to docker-compose.yml (existing)
  - Keycloak 26 image with dev mode
  - Health check configuration (6018a71)
  - Depends on PostgreSQL health
  - Mount realm import directory

- [x] Task: Create Keycloak realm configuration (existing)
  - Create `keycloak/tss-ppm-realm.json`
  - Define `tss-ppm` realm settings
  - Configure `tss-ppm-web` client (public, PKCE) (6018a71)
  - Configure `tss-ppm-api` client (bearer-only)
  - Set up role mappings: employee, manager, hr, admin

- [x] Task: Create test users in realm configuration (existing)
  - employee@tss.eu (employee role)
  - manager@tss.eu (manager role)
  - hr@tss.eu (hr role)
  - admin@tss.eu (admin role)
  - All with password: `test123`

- [x] Task: Set up custom TSS-PPM login theme (existing)
  - Create `keycloak/themes/tss-ppm/` directory
  - Add login theme with brand colors (Magenta/Navy)
  - Configure realm to use custom theme

- [x] Task: Verify Keycloak service and authentication (6018a71)
  - Run `docker compose up postgres keycloak`
  - Access admin console at localhost:8080
  - Verify realm imported correctly
  - Test login with test user credentials

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Keycloak Authentication Service' (Protocol in workflow.md)

---

## Phase 3: Application Services

### Objective
Add backend, frontend, and voice services to the Docker Compose configuration.

### Tasks

- [x] Task: Create backend Dockerfile for development (6018a71)
  - Update `backend/Dockerfile`
  - Python 3.12 slim base image
  - Install dependencies from requirements.txt
  - Configure uvicorn with hot reload

- [x] Task: Add backend service to docker-compose.yml (6018a71)
  - Build from backend Dockerfile
  - Volume mount for hot reload
  - Environment variables from .env
  - Health check on /health endpoint
  - Depends on db and keycloak health

- [x] Task: Create frontend development Dockerfile (existing)
  - Create `frontend/Dockerfile.dev`
  - Node.js 22 base image
  - Install dependencies
  - Run Vite dev server with host binding

- [x] Task: Add frontend service to docker-compose.yml (6018a71)
  - Build from frontend Dockerfile.dev
  - Volume mounts for source code (hot reload)
  - Environment variables for API URL and Keycloak
  - Depends on backend health

- [x] Task: Add voice service to docker-compose.yml (existing)
  - faster-whisper-server:latest-cpu image
  - Configure whisper-small model
  - Accessible on port 8001

- [x] Task: Verify all application services start (6018a71)
  - Run `docker compose up`
  - Confirm all 5 services healthy
  - Check logs for errors

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Application Services' (Protocol in workflow.md)

---

## Phase 4: Integration & Developer Experience

### Objective
Complete the setup with environment configuration, add health endpoint to backend, and verify full stack functionality.

### Tasks

- [x] Task: Add health check endpoint to backend (existing)
  - GET /health endpoint in FastAPI
  - Returns service status
  - GET /ready endpoint verifies database connectivity
  - Used by Docker health check

- [x] Task: Update .env.example with all variables (existing)
  - Database configuration
  - Keycloak URLs and client IDs
  - Voice service URL
  - CORS origins for local development

- [x] Task: Create .env from .env.example with dev defaults (6018a71)
  - Copy and configure for local development
  - Already in .gitignore

- [x] Task: Test complete authentication flow (6018a71)
  - Start full stack with `docker compose up`
  - Access frontend at localhost:5173
  - Login with test user via Keycloak
  - Verify JWT token passed to backend

- [x] Task: Test voice service integration (6018a71)
  - Verify voice endpoint responds
  - Test transcription with sample audio (manual)

- [x] Task: Document local development setup (6018a71)
  - Update README.md with setup instructions
  - Document test user credentials
  - List all service URLs and ports
  - Troubleshooting common issues

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration & Developer Experience' (Protocol in workflow.md)

---

## Completion Checklist

- [x] docker-compose.yml created with all 5 services
- [x] Database schema initialization working
- [x] Keycloak realm with test users configured
- [x] Custom login theme applied
- [x] Backend hot reload functional (with --reload flag)
- [x] Frontend hot reload functional
- [x] Voice service configured
- [x] Full authentication flow working
- [x] Documentation complete
