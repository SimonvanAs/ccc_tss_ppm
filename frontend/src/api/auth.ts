// TSS PPM v3.0 - Keycloak Authentication Service
import Keycloak from 'keycloak-js'

// Keycloak configuration
const keycloakConfig = {
  url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'tss-ppm',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'tss-ppm-frontend',
}

// Keycloak instance
let keycloak: Keycloak | null = null

/**
 * Initialize Keycloak authentication.
 * @returns Promise that resolves when authentication is complete
 */
export async function initAuth(): Promise<boolean> {
  keycloak = new Keycloak(keycloakConfig)

  try {
    const authenticated = await keycloak.init({
      onLoad: 'login-required',
      checkLoginIframe: false,
      pkceMethod: 'S256',
    })
    return authenticated
  } catch (error) {
    console.error('Keycloak initialization failed:', error)
    return false
  }
}

/**
 * Get the current access token.
 * Automatically refreshes if about to expire.
 */
export async function getToken(): Promise<string | null> {
  if (!keycloak) {
    return null
  }

  // Refresh token if it expires in less than 30 seconds
  try {
    await keycloak.updateToken(30)
    return keycloak.token || null
  } catch (error) {
    console.error('Failed to refresh token:', error)
    await keycloak.login()
    return null
  }
}

/**
 * Get the current user's profile.
 */
export function getCurrentUser() {
  if (!keycloak || !keycloak.tokenParsed) {
    return null
  }

  const token = keycloak.tokenParsed as {
    sub?: string
    email?: string
    name?: string
    realm_access?: { roles?: string[] }
    opco_id?: string
  }

  return {
    id: token.sub || '',
    email: token.email || '',
    name: token.name || '',
    roles: token.realm_access?.roles || [],
    opcoId: token.opco_id,
  }
}

/**
 * Check if user has a specific role.
 */
export function hasRole(role: string): boolean {
  const user = getCurrentUser()
  return user?.roles.includes(role) || false
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return keycloak?.authenticated || false
}

/**
 * Logout the current user.
 */
export function logout(): void {
  keycloak?.logout()
}

/**
 * Get the Keycloak instance (for advanced use).
 */
export function getKeycloak(): Keycloak | null {
  return keycloak
}
