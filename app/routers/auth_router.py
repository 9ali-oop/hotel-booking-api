"""
Authentication endpoints.

Provides a token issuance endpoint following the OAuth2 client-credentials
pattern. Clients exchange a valid API key for a short-lived JWT token,
which can then be used to authenticate subsequent write operations.

This two-step flow is standard in production APIs:
  1. Service obtains a token (POST /auth/token)
  2. Service uses the token for subsequent requests (Authorization: Bearer ...)

Tokens expire after 30 minutes by default, following the principle of
least privilege — limiting the damage window if a token is compromised.
"""

import hmac
from fastapi import APIRouter, HTTPException, status
from app.auth import (
    API_KEY, TokenRequest, TokenResponse, create_jwt_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtain a JWT access token",
    description="Exchange a valid API key for a short-lived JWT Bearer token. "
                "The token can then be used in the Authorization header for "
                "write operations. Tokens expire after 30 minutes.",
    responses={
        200: {
            "description": "JWT token issued successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIs...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "issued_at": "2025-03-07T10:00:00+00:00",
                        "expires_at": "2025-03-07T10:30:00+00:00",
                    }
                }
            },
        },
        403: {"description": "Invalid API key"},
    },
)
def obtain_token(body: TokenRequest):
    """
    Issue a JWT token in exchange for a valid API key.

    The issued token contains:
      - sub (subject): identifies the token holder
      - iss (issuer): the API name
      - iat (issued at): timestamp of issuance
      - exp (expires): token expiry timestamp

    Use the token in subsequent requests:
        Authorization: Bearer <access_token>
    """
    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(body.api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key. Cannot issue token.",
        )

    token_data = create_jwt_token(subject="authenticated_user")

    return TokenResponse(
        access_token=token_data["access_token"],
        token_type="bearer",
        expires_in=token_data["expires_in"],
        issued_at=token_data["issued_at"],
        expires_at=token_data["expires_at"],
    )
