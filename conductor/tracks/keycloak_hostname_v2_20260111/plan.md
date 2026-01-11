# Implementation Plan: Keycloak Hostname Configuration Migration (v1 → v2)

## Phase 1: Research & Analysis [checkpoint: d610709]

- [x] Task: Analyze current Keycloak configuration
  - [x] Read current docker-compose.yml Keycloak environment variables
  - [x] Document all hostname-related options currently in use
  - [x] Identify deprecated v1 options that need removal
  - **Findings:**
    - Current: `KC_HOSTNAME: localhost`, `KC_HOSTNAME_PORT: 8080`
    - Deprecated v1 option: `KC_HOSTNAME_PORT` must be removed
    - `KC_HOSTNAME` needs to be updated to v2 format (include port if needed)

- [x] Task: Research Keycloak 26 v2 hostname configuration
  - [x] Review Keycloak 26 documentation for v2 hostname options
  - [x] Document required v2 options: `hostname`, `hostname-admin`, `hostname-strict`, `hostname-backchannel-dynamic`
  - [x] Determine correct configuration for development (localhost) environment
  - **Findings:**
    - v2 Options:
      - `KC_HOSTNAME`: Full URL or just hostname (e.g., `http://localhost:8080` or `localhost`)
      - `KC_HOSTNAME_ADMIN`: Full URL for admin console (optional, only if different)
      - `KC_HOSTNAME_STRICT`: Default `true`, but `start-dev` defaults to `false`
      - `KC_HOSTNAME_BACKCHANNEL_DYNAMIC`: For dynamic backchannel resolution (default `false`)
      - `KC_HOSTNAME_DEBUG`: Enable debug page at /realms/master/hostname-debug
    - **Deprecated/Removed in v2:** `KC_HOSTNAME_PORT` - must include port in URL if needed
    - **Dev config recommendation:** Remove `KC_HOSTNAME_PORT`, use `KC_HOSTNAME: http://localhost:8080`
    - **Note:** `start-dev` mode already uses `hostname-strict=false` by default

- [x] Task: Conductor - User Manual Verification 'Research & Analysis' (Protocol in workflow.md)

## Phase 2: Development Configuration Update [checkpoint: e9d3b6e]

- [x] Task: Write integration test for Keycloak configuration (Red Phase)
  - [x] Create test file `backend/tests/test_keycloak_config.py`
  - [x] Write test to verify `.well-known/openid-configuration` endpoint responds
  - [x] Write test to verify issuer URL matches expected hostname
  - [x] Write test to verify token endpoint URL is correct
  - [x] Run tests - Keycloak endpoints work but logs show ERROR for deprecated v1 options

- [x] Task: Update docker-compose Keycloak configuration (Green Phase)
  - [x] Remove deprecated `hostname-port` option
  - [x] Configure v2 `hostname` option: `KC_HOSTNAME: http://localhost:8080`
  - [x] No additional v2 options needed (start-dev defaults are sufficient)
  - [x] Restart Keycloak and verify no hostname ERROR in logs

- [x] Task: Verify integration tests pass
  - [x] Run integration tests against updated Keycloak
  - [x] All 4 tests pass (Green Phase complete)

- [x] Task: Conductor - User Manual Verification 'Development Configuration Update' (Protocol in workflow.md)

## Phase 3: Production Configuration Template

- [ ] Task: Create production configuration template
  - [ ] Create `keycloak/README.md` with configuration documentation
  - [ ] Document v2 hostname options and their purpose
  - [ ] Provide example configuration for reverse proxy deployment
  - [ ] Provide example configuration for direct access deployment

- [ ] Task: Add migration notes
  - [ ] Document steps to migrate from v1 to v2 configuration
  - [ ] List breaking changes and considerations
  - [ ] Include rollback procedure if needed

- [ ] Task: Conductor - User Manual Verification 'Production Configuration Template' (Protocol in workflow.md)

## Phase 4: Final Verification & Cleanup

- [ ] Task: End-to-end login flow verification
  - [ ] Test complete login flow: Frontend → Keycloak → Callback
  - [ ] Verify token contains correct issuer
  - [ ] Test logout flow

- [ ] Task: Log verification
  - [ ] Restart all services with `docker compose down && docker compose up -d`
  - [ ] Verify no hostname-related ERROR messages in Keycloak logs
  - [ ] Verify no unexpected WARN messages (dev-mode warnings acceptable)

- [ ] Task: Conductor - User Manual Verification 'Final Verification & Cleanup' (Protocol in workflow.md)
