// Plausible Analytics composable
// Provides event tracking with graceful degradation when not configured

declare global {
  interface Window {
    plausible?: (
      event: string,
      options?: { props?: Record<string, string | number | boolean> }
    ) => void
  }
}

// Analytics event names for type safety
export type AnalyticsEvent =
  | 'goal_save'
  | 'review_submit'
  | 'employee_signature'
  | 'manager_signature'
  | 'calibration_complete'
  | 'pdf_download'

// Configuration from environment
const PLAUSIBLE_DOMAIN = import.meta.env.VITE_PLAUSIBLE_DOMAIN as string | undefined
const PLAUSIBLE_URL = (import.meta.env.VITE_PLAUSIBLE_URL as string) || 'https://plausible.io'

// Track if script has been injected
let scriptInjected = false

/**
 * Inject Plausible script into the page
 * Only injects once and only if domain is configured
 */
function injectPlausibleScript(): void {
  if (scriptInjected || !PLAUSIBLE_DOMAIN) return

  const script = document.createElement('script')
  script.defer = true
  script.dataset.domain = PLAUSIBLE_DOMAIN
  script.src = `${PLAUSIBLE_URL}/js/script.js`
  document.head.appendChild(script)

  scriptInjected = true
}

/**
 * Check if analytics is enabled
 */
export function isAnalyticsEnabled(): boolean {
  return Boolean(PLAUSIBLE_DOMAIN)
}

/**
 * Track a custom event
 * Safe to call even when analytics is not configured
 */
export function trackEvent(
  event: AnalyticsEvent,
  props?: Record<string, string | number | boolean>
): void {
  if (!PLAUSIBLE_DOMAIN) return

  // Ensure script is loaded
  injectPlausibleScript()

  // Use Plausible's queue pattern for events before script loads
  window.plausible?.(event, props ? { props } : undefined)
}

/**
 * Track a page view
 * Called automatically by router, but can be called manually
 */
export function trackPageView(path?: string): void {
  if (!PLAUSIBLE_DOMAIN) return

  // Ensure script is loaded
  injectPlausibleScript()

  // Plausible auto-tracks page views, but we can trigger manually if needed
  window.plausible?.('pageview', path ? { props: { path } } : undefined)
}

/**
 * Initialize analytics
 * Call once at app startup to inject the script early
 */
export function initAnalytics(): void {
  if (!PLAUSIBLE_DOMAIN) {
    console.debug('[Analytics] Plausible not configured (VITE_PLAUSIBLE_DOMAIN not set)')
    return
  }

  console.debug(`[Analytics] Initializing Plausible for domain: ${PLAUSIBLE_DOMAIN}`)
  injectPlausibleScript()
}

/**
 * Composable for analytics
 * Provides reactive access to analytics functions
 */
export function useAnalytics() {
  return {
    isEnabled: isAnalyticsEnabled(),
    trackEvent,
    trackPageView,
  }
}
