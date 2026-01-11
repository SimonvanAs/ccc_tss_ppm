# Implementation Plan: Keycloak Hostname Configuration Migration (v1 → v2)

## Phase 1: Research & Analysis

- [ ] Task: Analyze current Keycloak configuration
  - [ ] Read current docker-compose.yml Keycloak environment variables
  - [ ] Document all hostname-related options currently in use
  - [ ] Identify deprecated v1 options that need removal

- [ ] Task: Research Keycloak 26 v2 hostname configuration
  - [ ] Review Keycloak 26 documentation for v2 hostname options
  - [ ] Document required v2 options: `hostname`, `hostname-admin`, `hostname-strict`, `hostname-backchannel-dynamic`
  - [ ] Determine correct configuration for development (localhost) environment

- [ ] Task: Conductor - User Manual Verification 'Research & Analysis' (Protocol in workflow.md)

## Phase 2: Development Configuration Update

- [ ] Task: Write integration test for Keycloak configuration (Red Phase)
  - [ ] Create test file `backend/tests/test_keycloak_config.py`
  - [ ] Write test to verify `.well-known/openid-configuration` endpoint responds
  - [ ] Write test to verify issuer URL matches expected hostname
  - [ ] Write test to verify token endpoint URL is correct
  - [ ] Run tests and confirm they fail (Keycloak not yet configured)

- [ ] Task: Update docker-compose Keycloak configuration (Green Phase)
  - [ ] Remove deprecated `hostname-port` option
  - [ ] Remove or update `hostname-strict` option
  - [ ] Configure v2 `hostname` option for development
  - [ ] Add any additional required v2 options
  - [ ] Restart Keycloak and verify no hostname ERROR/WARN in logs

- [ ] Task: Verify integration tests pass
  - [ ] Run integration tests against updated Keycloak
  - [ ] Confirm all tests pass (Green Phase complete)

- [ ] Task: Conductor - User Manual Verification 'Development Configuration Update' (Protocol in workflow.md)

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
