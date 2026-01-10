# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TSS PPM (Performance Portfolio Management) v3.0 is an HR performance scoring web application that replaces Excel-based annual employee reviews. It uses a 9-grid scoring system (WHAT-axis × HOW-axis) with voice input, multi-language support (EN/NL/ES), and automated PDF-A report generation.

## Technology Stack

- **Frontend**: Vue 3 with Vite (SPA), TypeScript, vue-i18n
- **Backend**: Python (FastAPI) + PostgreSQL 17, asyncpg (raw SQL, no ORM)
- **Authentication**: Keycloak JS adapter v26 (OIDC/EntraID federation) with custom TSS-PPM theme
- **Voice Input**: faster-whisper Docker service (`fedirz/faster-whisper-server`) or configurable voice-to-text API
- **PDF**: WeasyPrint (integrated into backend)
- **Styling**: Tahoma font, brand colors: Magenta (#CC0E70), Navy Blue (#004A91)
- **Deployment**: Docker containers with Caddy reverse proxy for TLS

## Development Commands

### Full Stack (Docker)
```bash
docker compose up -d              # Start all services (postgres, keycloak, api, frontend, whisper)
docker compose down               # Stop all services
docker compose logs -f api        # Tail API logs
docker compose logs -f frontend   # Tail frontend logs
```

### Frontend (standalone)
```bash
cd frontend
npm install                       # Install dependencies
npm run dev                       # Start dev server (http://localhost:5173)
npm run build                     # Production build
npm run test                      # Run tests (Vitest)
npm run test:ui                   # Run tests with UI
npm run lint                      # ESLint
npm run type-check                # TypeScript type checking
```

### Backend (standalone)
```bash
cd backend
pip install -r requirements.txt   # Install dependencies
uvicorn src.main:app --reload     # Start dev server (http://localhost:8000)
pytest                            # Run all tests
pytest tests/test_scoring.py      # Run single test file
pytest -k "test_veto"             # Run tests matching pattern
```

### Database
```bash
# Connect to dev database
docker exec -it tss_ppm_db psql -U ppm -d tss_ppm

# Run migrations (SQL files in database/init/)
docker compose exec postgres psql -U ppm -d tss_ppm -f /docker-entrypoint-initdb.d/001_schema.sql
```

### Environment Setup
```bash
cp .env.example .env              # Create local env file
# Edit .env with local settings
```

## Service URLs (Development)
- Frontend: http://localhost:5173
- API: http://localhost:8000
- Keycloak Admin: http://localhost:8080 (admin/admin)
- Voice Service: http://localhost:8001

## Project Structure

```
├── frontend/               # Vue 3 SPA
│   ├── src/
│   │   ├── api/           # API client modules
│   │   ├── components/    # Vue components (common/, review/, dashboard/, calibration/)
│   │   ├── composables/   # Vue composables (useAuth, useReview, useAutoSave)
│   │   ├── views/         # Page components
│   │   ├── i18n/          # Translation JSON files (en, nl, es)
│   │   └── services/      # Keycloak, scoring logic
│   └── package.json
├── backend/               # Python FastAPI
│   ├── src/
│   │   ├── routers/       # API route handlers
│   │   ├── repositories/  # Raw SQL queries (asyncpg)
│   │   ├── services/      # Business logic (scoring, pdf, voice)
│   │   └── schemas/       # Pydantic models
│   └── requirements.txt
├── database/
│   ├── init/              # SQL migrations (run on startup)
│   └── seed/              # Sample data
├── keycloak/
│   ├── themes/tss-ppm/    # Custom login theme
│   └── tss-ppm-realm.json # Realm config with roles
└── docker-compose.yml
```

## Key Architectural Concepts

### Scoring System
- **WHAT-axis (Goals)**: Up to 9 weighted goals (must total 100%), scored 1-3. Goal types: Standard, KAR, SCF
- **HOW-axis (Competencies)**: 6 competencies per TOV level (A/B/C/D), each scored 1-3
- **VETO Rules**:
  - SCF goal scores 1 → entire WHAT score = 1.00
  - KAR goal scores 1 → triggers VETO, but can be compensated by another KAR goal scoring 3
  - Any competency scores 1 → entire HOW score = 1.00
- **9-Grid**: 3×3 matrix combining WHAT (rows) and HOW (columns), color-coded: Red, Orange, Green, Dark Green

### Multi-Tenancy
All data is isolated by OpCo (Operating Company). The `opco_id` is included in JWT claims and enforced on all queries.

### User Roles & RBAC
- **EMPLOYEE**: View/edit own goals, view reviews, sign own reviews
- **MANAGER**: Score team reviews, approve goal changes, view team dashboard (scope: `manager_id = current_user.id`)
- **HR**: View all reviews in OpCo, organization statistics, manage calibration sessions
- **ADMIN**: Manage OpCo settings, users, API credentials (no access to review content for GDPR)

See `requirements/RBAC-Matrix.md` for detailed permission matrix.

### Review Workflow
Each review has a **stage** (annual cycle phase) and **status** (signature progress):

**Stages**: GOAL_SETTING → MID_YEAR_REVIEW → END_YEAR_REVIEW

**Status flow**: DRAFT → PENDING_EMPLOYEE_SIGNATURE → EMPLOYEE_SIGNED → PENDING_MANAGER_SIGNATURE → MANAGER_SIGNED → SIGNED → ARCHIVED

See `requirements/Review-Workflow-States.md` for full state machine.

### Competency Framework
The HOW-axis uses the IDE Competency Framework: 3 categories × 2 subcategories × 4 levels (A-D):
- **Dedicated**: Result driven, Committed
- **Entrepreneurial**: Entrepreneurial, Ambition
- **Innovative**: Market oriented, Customer focused

Full data in `requirements/IDE-Competency-Framework.md`

### API Design
- RESTful endpoints at `/api/v1/*`
- JWT validation via Keycloak
- Raw SQL with asyncpg (no ORM)
- All mutations logged to `audit_logs` table

## Multi-Language Support

- UI translations: `frontend/src/i18n/*.json` (EN/NL/ES)
- Competency translations: stored in database (allows HR to customize per OpCo)
- Language priority: User preference → OpCo default → Browser → English fallback

## Voice Input

Hold-to-dictate component (`VoiceInput.vue`):
- Visual states: Idle (grey), Recording (magenta pulse), Processing (blue spinner), Error (red shake)
- Appends transcription to existing text
- Uses `fedirz/faster-whisper-server` Docker image with whisper-small model

## Key Files Reference

| File | Purpose |
|------|---------|
| `requirements/TSS-PPM-Requirements.md` | Full requirements specification |
| `requirements/RBAC-Matrix.md` | Detailed permissions per role |
| `requirements/Review-Workflow-States.md` | State machine documentation |
| `requirements/IDE-Competency-Framework.md` | 24 competencies × 3 languages |
| `architecture/TSS-PPM-Architecture.md` | System architecture with diagrams |
| `keycloak/tss-ppm-realm.json` | Keycloak realm config |
