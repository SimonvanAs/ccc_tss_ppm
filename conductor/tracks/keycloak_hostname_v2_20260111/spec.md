# Specification: Keycloak Hostname Configuration Migration (v1 → v2)

## Overview

Migrate Keycloak from deprecated v1 hostname configuration options to v2 hostname configuration, eliminating ERROR and WARN log messages while aligning with Keycloak 26 best practices. This includes updating both development (docker-compose) and production configuration templates.

## Background

Keycloak 26 has deprecated the v1 hostname configuration options. The current configuration produces:
- **ERROR**: `Hostname v1 options [hostname-port] are still in use, please review your configuration`
- **WARN**: `If hostname is specified, hostname-strict is effectively ignored`

## Functional Requirements

### FR-1: Remove Deprecated v1 Options
- Remove `hostname-port` option from Keycloak configuration
- Remove any other deprecated v1 hostname options

### FR-2: Implement v2 Hostname Configuration
- Configure `hostname` option using v2 format (full URL or hostname)
- Review and properly configure `hostname-strict` setting
- Configure `hostname-admin` if admin console requires different URL
- Configure `hostname-backchannel-dynamic` if needed for backend communications

### FR-3: Update Development Configuration
- Update `docker-compose.yml` Keycloak service environment variables
- Ensure development setup works with `localhost:8080`

### FR-4: Create Production Configuration Template
- Document production hostname configuration in a template or README
- Include examples for common deployment scenarios (reverse proxy, direct access)

## Non-Functional Requirements

### NFR-1: Zero Downtime Migration
- Configuration changes should not require data migration
- Existing sessions and tokens should remain valid

### NFR-2: Clean Logs
- No ERROR or WARN messages related to hostname configuration on startup

### NFR-3: Documentation
- Document the v2 hostname configuration options and their purpose
- Provide migration notes for any existing deployments

## Acceptance Criteria

1. **AC-1**: Keycloak starts without any hostname-related ERROR messages
2. **AC-2**: Keycloak starts without hostname-related WARN messages (except expected dev-mode warnings)
3. **AC-3**: Login flow works correctly in development environment (localhost:5173 → Keycloak → callback)
4. **AC-4**: OpenID Connect discovery endpoint (`.well-known/openid-configuration`) returns correct URLs
5. **AC-5**: Token endpoint URLs in discovery document match configured hostname
6. **AC-6**: Production configuration template exists with documented options
7. **AC-7**: Automated integration test validates Keycloak configuration endpoints

## Out of Scope

- Keycloak version upgrade (staying on 26.x)
- Changes to realm configuration or client settings
- TLS/HTTPS configuration changes (handled by Caddy reverse proxy)
- EntraID federation configuration changes
