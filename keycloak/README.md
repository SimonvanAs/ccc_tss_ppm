# Keycloak Configuration

This directory contains Keycloak configuration files for TSS PPM v3.0.

## Contents

- `tss-ppm-realm.json` - Realm configuration with roles and clients
- `themes/tss-ppm/` - Custom login theme with TSS branding

## Hostname Configuration (v2)

Keycloak 26 uses v2 hostname configuration. The v1 options (`hostname-port`, `hostname-strict-https`, etc.) are deprecated and removed.

### Configuration Options

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `hostname` | `KC_HOSTNAME` | Full URL or hostname for Keycloak. Required in production. |
| `hostname-admin` | `KC_HOSTNAME_ADMIN` | Full URL for admin console (if different from hostname) |
| `hostname-strict` | `KC_HOSTNAME_STRICT` | Disable dynamic hostname resolution. Default: `true` |
| `hostname-backchannel-dynamic` | `KC_HOSTNAME_BACKCHANNEL_DYNAMIC` | Enable dynamic backchannel URL resolution. Default: `false` |
| `hostname-debug` | `KC_HOSTNAME_DEBUG` | Enable debug page at `/realms/master/hostname-debug` |

### Development Configuration

For local development with `start-dev`:

```yaml
# docker-compose.yml
keycloak:
  image: quay.io/keycloak/keycloak:26.0
  command: start-dev --import-realm
  environment:
    KC_HOSTNAME: http://localhost:8080
    KC_HTTP_ENABLED: "true"
```

**Note:** In dev mode, `hostname-strict` defaults to `false`, allowing dynamic hostname resolution.

### Production Configuration (Reverse Proxy)

For production behind a reverse proxy (e.g., Caddy, nginx):

```yaml
# docker-compose.yml
keycloak:
  image: quay.io/keycloak/keycloak:26.0
  command: start --import-realm
  environment:
    KC_HOSTNAME: https://auth.example.com
    KC_PROXY_HEADERS: forwarded
    KC_HTTP_ENABLED: "true"
    KC_DB: postgres
    KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
    KC_DB_USERNAME: ${KC_DB_USER}
    KC_DB_PASSWORD: ${KC_DB_PASSWORD}
```

```
# Caddyfile
auth.example.com {
    reverse_proxy keycloak:8080
}
```

### Production Configuration (Direct Access)

For production with direct HTTPS access:

```yaml
# docker-compose.yml
keycloak:
  image: quay.io/keycloak/keycloak:26.0
  command: start --import-realm
  environment:
    KC_HOSTNAME: https://auth.example.com
    KC_HTTPS_CERTIFICATE_FILE: /opt/keycloak/conf/server.crt
    KC_HTTPS_CERTIFICATE_KEY_FILE: /opt/keycloak/conf/server.key
    KC_DB: postgres
    KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
    KC_DB_USERNAME: ${KC_DB_USER}
    KC_DB_PASSWORD: ${KC_DB_PASSWORD}
  ports:
    - "443:8443"
  volumes:
    - ./certs:/opt/keycloak/conf:ro
```

### Admin Console on Different URL

If the admin console needs to be on a different URL:

```yaml
environment:
  KC_HOSTNAME: https://auth.example.com
  KC_HOSTNAME_ADMIN: https://admin.example.com
```

## Migration from v1 to v2

### Breaking Changes

1. **`hostname-port` removed** - Include port in the hostname URL instead
   - Before: `KC_HOSTNAME=localhost` + `KC_HOSTNAME_PORT=8080`
   - After: `KC_HOSTNAME=http://localhost:8080`

2. **`hostname-strict-https` removed** - Use `hostname-strict` instead

3. **`hostname-path` removed** - Include path in the hostname URL

4. **URL format required** - For non-standard ports, use full URL format

### Migration Steps

1. Remove deprecated options:
   - `KC_HOSTNAME_PORT`
   - `KC_HOSTNAME_STRICT_HTTPS`
   - `KC_HOSTNAME_PATH`

2. Update `KC_HOSTNAME` to full URL format if using non-standard port:
   ```yaml
   # Before
   KC_HOSTNAME: localhost
   KC_HOSTNAME_PORT: 8080

   # After
   KC_HOSTNAME: http://localhost:8080
   ```

3. Restart Keycloak and verify:
   - No ERROR messages about "Hostname v1 options"
   - OIDC discovery endpoint returns correct URLs
   - Login flow works correctly

### Rollback Procedure

If issues occur after migration:

1. Revert docker-compose.yml to previous version
2. Restart Keycloak: `docker compose up -d --force-recreate keycloak`
3. Verify login flow works
4. Investigate and fix v2 configuration before retrying

## Verification

### Check for Configuration Errors

```bash
# Check Keycloak logs for hostname errors
docker logs tss_ppm_auth 2>&1 | grep -E "ERROR.*hostname"
```

### Verify OIDC Discovery

```bash
# Check discovery endpoint
curl -s http://localhost:8080/realms/tss-ppm/.well-known/openid-configuration | jq '.issuer, .token_endpoint'
```

### Debug Hostname Issues

Enable hostname debug page:

```yaml
environment:
  KC_HOSTNAME_DEBUG: "true"
```

Then access: `http://localhost:8080/realms/master/hostname-debug`

## References

- [Keycloak Hostname v2 Documentation](https://www.keycloak.org/server/hostname)
- [Keycloak 26 Release Notes](https://www.keycloak.org/2024/10/keycloak-2600-released)
- [Keycloak Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/index.html)
