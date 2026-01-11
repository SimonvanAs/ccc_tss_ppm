# TSS PPM v3.0 - Configuration
"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = os.getenv(
        'DATABASE_URL',
        'postgresql://ppm:ppm_dev_password@localhost:5432/tss_ppm'
    )

    # Keycloak
    # Internal URL for fetching JWKS (inside Docker network)
    keycloak_url: str = os.getenv('KEYCLOAK_URL', 'http://localhost:8080')
    keycloak_realm: str = os.getenv('KEYCLOAK_REALM', 'tss-ppm')
    keycloak_client_id: str = os.getenv('KEYCLOAK_CLIENT_ID', 'tss-ppm-api')
    # External URL for issuer validation (how clients access Keycloak)
    keycloak_issuer_url: str = os.getenv('KEYCLOAK_ISSUER_URL', 'http://localhost:8080')

    # CORS
    cors_origins: list[str] = None

    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')

    def __post_init__(self):
        """Parse comma-separated values after initialization."""
        if self.cors_origins is None:
            origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173')
            self.cors_origins = [o.strip() for o in origins.split(',')]

    @property
    def keycloak_issuer(self) -> str:
        """Get the Keycloak issuer URL (external, as seen by clients)."""
        return f'{self.keycloak_issuer_url}/realms/{self.keycloak_realm}'

    @property
    def keycloak_jwks_url(self) -> str:
        """Get the Keycloak JWKS URL for token verification (internal)."""
        return f'{self.keycloak_url}/realms/{self.keycloak_realm}/protocol/openid-connect/certs'


# Global settings instance
settings = Settings()
