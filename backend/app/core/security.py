"""Security utilities for JWT and password handling.

REQ-SEC-004: Role-based access control
NFR-SEC-010: Authentication required for admin access
NFR-SEC-012: Session security - token expiry, refresh mechanism
AC-SEC-001: RBAC blocks unauthorized actions
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cache for the JWT secret key (generated once if not configured)
_cached_jwt_secret: str | None = None


def get_jwt_secret_key() -> str:
    """Get JWT secret key from settings or generate a random one for dev.

    NFR-SEC-022: Secrets managed via environment variables.
    Note: For development, a random key is generated once and cached.
    For production, always set JWT_SECRET_KEY environment variable.
    """
    global _cached_jwt_secret

    if settings.jwt_secret_key:
        return settings.jwt_secret_key

    # Generate and cache random key for development (not recommended for production)
    if _cached_jwt_secret is None:
        _cached_jwt_secret = secrets.token_urlsafe(32)
    return _cached_jwt_secret


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to compare against.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token.

    NFR-SEC-012: Tokens must expire.
    Default expiry: 15 minutes.

    Args:
        data: Payload data to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    })

    encoded_jwt = jwt.encode(
        to_encode,
        get_jwt_secret_key(),
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token.

    NFR-SEC-012: Refresh mechanism must be secure.
    Default expiry: 7 days.

    Args:
        data: Payload data to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT refresh token string.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    })

    encoded_jwt = jwt.encode(
        to_encode,
        get_jwt_secret_key(),
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict[str, Any] | None:
    """Verify and decode a JWT token.

    NFR-SEC-012: Session security validation.

    Args:
        token: JWT token string to verify.
        token_type: Expected token type ('access' or 'refresh').

    Returns:
        Decoded token payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            get_jwt_secret_key(),
            algorithms=[settings.jwt_algorithm],
        )

        # Verify token type
        if payload.get("type") != token_type:
            return None

        return payload
    except JWTError:
        return None
