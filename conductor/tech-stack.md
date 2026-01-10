# Technology Stack: TSS PPM v3.0

## Overview

TSS PPM uses a modern, containerized architecture with a Vue 3 frontend, Python FastAPI backend, and PostgreSQL database. The stack prioritizes minimal dependencies, raw SQL for database access, and Docker-based deployment.

## Frontend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | Vue 3 | ^3.5.13 | Reactive UI components with Composition API |
| **Build Tool** | Vite | ^6.0.7 | Fast development server and optimized builds |
| **Language** | TypeScript | ^5.7.2 | Type-safe JavaScript |
| **Routing** | vue-router | ^4.5.0 | Client-side SPA routing |
| **Internationalization** | vue-i18n | ^10.0.5 | Multi-language support (EN/NL/ES) |
| **Authentication** | keycloak-js | ^26.0.0 | OIDC client for Keycloak integration |
| **Testing** | Vitest | ^2.1.8 | Unit and component testing |
| **Linting** | ESLint | ^9.17.0 | Code quality and style enforcement |
| **Vue Linting** | eslint-plugin-vue | ^9.32.0 | Vue-specific linting rules |
| **Type Checking** | vue-tsc | ^2.2.0 | TypeScript checking for Vue SFCs |

### Frontend Commands
```bash
npm run dev          # Start development server (localhost:5173)
npm run build        # Production build
npm run test         # Run tests with Vitest
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

## Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.115.6 | Async Python web framework with OpenAPI |
| **ASGI Server** | Uvicorn | 0.34.0 | High-performance async server |
| **Database Driver** | asyncpg | 0.30.0 | Async PostgreSQL driver (raw SQL) |
| **Authentication** | PyJWT | 2.10.1 | JWT token validation |
| **PDF Generation** | WeasyPrint | 63.1 | PDF-A report generation |
| **Testing** | pytest | 8.3.4 | Test framework |
| **Async Testing** | pytest-asyncio | 0.25.2 | Async test support |
| **HTTP Client** | httpx | 0.28.1 | Async HTTP client for testing |

### Backend Commands
```bash
uvicorn src.main:app --reload   # Start development server (localhost:8000)
pytest                          # Run all tests
pytest -k "test_name"           # Run specific test
```

### Design Decisions
- **No ORM**: Raw SQL with asyncpg for full control and performance
- **Minimal Dependencies**: Only essential packages to reduce maintenance burden
- **Async-First**: All database and HTTP operations are async

## Database

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Database** | PostgreSQL | 17-alpine | Primary data store |

### Database Access
```bash
docker exec -it tss_ppm_db psql -U ppm -d tss_ppm
```

### Schema Management
- SQL migration files in `database/init/`
- Executed automatically on container startup
- Seed data in `database/seed/`

## Authentication

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Identity Provider** | Keycloak | 26.0 | OIDC/OAuth2 authentication |
| **Federation** | EntraID | - | Enterprise SSO integration |
| **Theme** | Custom TSS-PPM | - | Branded login pages |

### Keycloak Configuration
- Realm: `tss-ppm`
- Clients: `tss-ppm-web` (public), `tss-ppm-api` (bearer-only)
- Roles: `employee`, `manager`, `hr`, `admin`
- Custom attribute: `opco_id` for multi-tenancy

## Voice Service

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Speech-to-Text** | faster-whisper-server | latest-cpu | Voice transcription |
| **Model** | Systran/faster-whisper-small | - | Whisper small model |

### Configuration
- Runs on port 8001
- Supports EN/NL/ES languages
- CPU-based inference (int8 compute type)

## Infrastructure

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Reverse Proxy** | Caddy | 2-alpine | TLS termination, routing |
| **Containerization** | Docker Compose | - | Service orchestration |

### Service Ports (Development)
| Service | Port |
|---------|------|
| Frontend | 5173 |
| API | 8000 |
| Keycloak | 8080 |
| Voice | 8001 |
| PostgreSQL | 5432 |

## Development Environment

### Prerequisites
- Docker and Docker Compose
- Node.js (for frontend development outside Docker)
- Python 3.11+ (for backend development outside Docker)

### Quick Start
```bash
cp .env.example .env           # Configure environment
docker compose up -d           # Start all services
```

### Environment Variables
Key environment variables are defined in `.env.example`:
- Database connection (`DB_USER`, `DB_PASSWORD`, `DB_NAME`)
- Keycloak settings (`KC_ADMIN`, `KC_ADMIN_PASSWORD`)
- API configuration (`CORS_ORIGINS`, `LOG_LEVEL`)

## Testing Strategy

| Layer | Tool | Coverage Target |
|-------|------|-----------------|
| Frontend Unit | Vitest | >80% |
| Backend Unit | pytest | >80% |
| Backend Async | pytest-asyncio | - |
| API Integration | httpx + pytest | - |

## Future Considerations

- GPU-accelerated voice service (`faster-whisper-server:latest-cuda`)
- Redis for session caching (if needed for scale)
- Playwright for E2E testing
