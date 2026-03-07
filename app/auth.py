"""
Authentication and authorisation module.

Implements a dual authentication strategy:

  1. API Key authentication (X-API-Key header)
     — Simple, stateless, ideal for service-to-service communication.
     — Key is verified using constant-time comparison to prevent timing attacks.

  2. JWT Bearer token authentication (Authorization: Bearer <token>)
     — Industry-standard token-based auth (RFC 7519).
     — Tokens are issued via POST /auth/token with a valid API key.
     — Tokens include expiry (exp), issuer (iss), and subject (sub) claims.
     — Short-lived tokens (30 min default) follow the principle of least privilege.

Security design decisions:
  - Write endpoints (POST, PUT, PATCH, DELETE) require authentication.
  - Read endpoints (GET) remain public for ease of API exploration.
  - API keys are compared using hmac.compare_digest (constant-time)
    to prevent timing side-channel attacks.
  - JWT secret is derived from the API key via SHA-256 hashing, so
    changing the API key automatically invalidates all existing tokens.
  - The /auth/token endpoint rate-limits login attempts via slowapi.

This proportionate security model balances real-world best practices
with the practical needs of a coursework API that must be demonstrable.

Author: Ali
Module: COMP3011 Web Services and Web Data
"""

import hmac
import hashlib
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# JWT implementation using PyJWT (lightweight, no heavy crypto dependencies)
# Falls back to a simple HMAC-based token if PyJWT is not installed.
# ---------------------------------------------------------------------------
try:
    import jwt as pyjwt
    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("API_KEY", "hotel-booking-dev-key-2025")

# JWT secret derived from the API key — changing the key invalidates tokens
JWT_SECRET = hashlib.sha256(API_KEY.encode()).hexdigest()
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = int(os.environ.get("JWT_EXPIRY_MINUTES", "30"))
JWT_ISSUER = "hotel-booking-intelligence-api"

# ---------------------------------------------------------------------------
# Security schemes — these appear in Swagger UI's "Authorize" dialog
# ---------------------------------------------------------------------------
api_key_header = APIKeyHeader(
    name="X-API-Key",
    description=(
        "API key for write operations. "
        "Default dev key: hotel-booking-dev-key-2025"
    ),
    auto_error=False,
)

bearer_scheme = HTTPBearer(
    description=(
        "JWT Bearer token obtained from POST /auth/token. "
        "Tokens expire after 30 minutes."
    ),
    auto_error=False,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class TokenRequest(BaseModel):
    """Request body for obtaining a JWT token."""
    api_key: str


class TokenResponse(BaseModel):
    """Response containing the issued JWT token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    issued_at: str
    expires_at: str


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_jwt_token(subject: str = "api_user") -> dict:
    """
    Create a signed JWT token with standard claims.

    Returns a dict with the token string and metadata.
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=JWT_EXPIRY_MINUTES)

    payload = {
        "sub": subject,
        "iss": JWT_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }

    if HAS_PYJWT:
        token = pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    else:
        # Fallback: simple HMAC token (base64-encoded)
        import base64, json
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        sig = hmac.new(JWT_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()
        token = base64.urlsafe_b64encode(payload_bytes).decode() + "." + sig

    return {
        "access_token": token,
        "expires_in": JWT_EXPIRY_MINUTES * 60,
        "issued_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    }


def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Returns the decoded payload if valid.
    Raises HTTPException if expired, invalid, or tampered with.
    """
    if HAS_PYJWT:
        try:
            payload = pyjwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
                issuer=JWT_ISSUER,
            )
            return payload
        except pyjwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Request a new one from POST /auth/token.",
            )
        except pyjwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e}",
            )
    else:
        # Fallback verification
        import base64, json
        try:
            encoded_payload, sig = token.rsplit(".", 1)
            payload_bytes = base64.urlsafe_b64decode(encoded_payload)
            expected_sig = hmac.new(
                JWT_SECRET.encode(), payload_bytes, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig, expected_sig):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token signature.",
                )
            payload = json.loads(payload_bytes)
            if payload.get("exp", 0) < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired.",
                )
            return payload
        except (ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed token.",
            )


# ---------------------------------------------------------------------------
# Dependency — dual auth (API key OR Bearer token)
# ---------------------------------------------------------------------------
async def require_api_key(
    api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> str:
    """
    FastAPI dependency that enforces authentication via either:
      1. X-API-Key header, OR
      2. Authorization: Bearer <jwt_token>

    At least one must be provided and valid.

    Returns an identifier string for audit logging.

    Raises:
        HTTPException 401 if neither auth method is provided
        HTTPException 403 if API key is invalid
        HTTPException 401 if JWT token is expired or invalid
    """
    # Try API key first
    if api_key is not None:
        # Constant-time comparison prevents timing attacks
        if hmac.compare_digest(api_key, API_KEY):
            return "api_key_user"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    # Try Bearer token
    if bearer is not None:
        payload = verify_jwt_token(bearer.credentials)
        return payload.get("sub", "jwt_user")

    # Neither provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "Authentication required. Provide either: "
            "(1) X-API-Key header, or "
            "(2) Authorization: Bearer <token> from POST /auth/token."
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )
