"""Unit tests for security module.

REQ-SEC-004: Role-based access control
NFR-SEC-012: Session security - token expiry
AC-SEC-001: RBAC blocks unauthorized actions
"""

import time
from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password returns a bcrypt hash."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        # Bcrypt hashes start with $2b$ or $2a$
        assert hashed.startswith("$2")

    def test_hash_password_different_for_same_password(self):
        """Test that hashing same password creates different hashes (salting)."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Each hash should be unique due to random salt
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """Test that empty password can be hashed and verified."""
        password = ""
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("not_empty", hashed) is False


class TestJWTTokens:
    """Tests for JWT token creation and verification."""

    def test_create_access_token_basic(self):
        """Test basic access token creation."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        # JWT format: header.payload.signature
        assert len(token.split(".")) == 3

    def test_create_access_token_with_custom_expiry(self):
        """Test access token with custom expiration."""
        data = {"sub": "123"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))

        assert token is not None
        payload = verify_token(token)
        assert payload is not None

    def test_create_refresh_token_basic(self):
        """Test basic refresh token creation."""
        data = {"sub": "123"}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_verify_access_token_valid(self):
        """Test verification of valid access token."""
        data = {"sub": "123", "email": "test@example.com", "role": "host"}
        token = create_access_token(data)
        payload = verify_token(token, token_type="access")

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "host"
        assert payload["type"] == "access"

    def test_verify_refresh_token_valid(self):
        """Test verification of valid refresh token."""
        data = {"sub": "456"}
        token = create_refresh_token(data)
        payload = verify_token(token, token_type="refresh")

        assert payload is not None
        assert payload["sub"] == "456"
        assert payload["type"] == "refresh"

    def test_verify_token_wrong_type(self):
        """Test that verifying with wrong token type returns None.

        NFR-SEC-012: Token type validation.
        """
        data = {"sub": "123"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        # Verify access token as refresh should fail
        assert verify_token(access_token, token_type="refresh") is None

        # Verify refresh token as access should fail
        assert verify_token(refresh_token, token_type="access") is None

    def test_verify_token_invalid_token(self):
        """Test that invalid token returns None."""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)

        assert payload is None

    def test_verify_token_tampered_token(self):
        """Test that tampered token returns None.

        NFR-SEC-012: Session security.
        """
        data = {"sub": "123"}
        token = create_access_token(data)

        # Tamper with the token (modify payload)
        parts = token.split(".")
        tampered_token = f"{parts[0]}.tampered{parts[1]}.{parts[2]}"

        payload = verify_token(tampered_token)
        assert payload is None

    def test_token_expiry(self):
        """Test that expired token returns None.

        NFR-SEC-012: Tokens must expire.
        """
        data = {"sub": "123"}
        # Create token that expires in 1 second
        token = create_access_token(data, expires_delta=timedelta(seconds=1))

        # Token should be valid immediately
        payload = verify_token(token)
        assert payload is not None

        # Wait for expiration
        time.sleep(2)

        # Token should now be invalid
        payload = verify_token(token)
        assert payload is None

    def test_token_contains_issued_at(self):
        """Test that token contains issued_at (iat) claim."""
        data = {"sub": "123"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload is not None
        assert "iat" in payload
        assert "exp" in payload

    def test_token_preserves_custom_claims(self):
        """Test that custom claims are preserved in token."""
        data = {
            "sub": "123",
            "email": "test@example.com",
            "role": "manager",
            "restaurant_id": 456,
        }
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "manager"
        assert payload["restaurant_id"] == 456
