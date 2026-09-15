"""Validate Microsoft Entra access tokens."""

from __future__ import annotations

from typing import Any, Dict, Optional

import jwt
from jwt import PyJWKClient

from entra_auth.config import api_audiences, issuer, jwks_url, tenant_id

_jwk_client: Optional[PyJWKClient] = None
_jwk_tenant: str = ""


def _get_jwk_client() -> PyJWKClient:
    global _jwk_client, _jwk_tenant
    tid = tenant_id()
    if _jwk_client is None or _jwk_tenant != tid:
        _jwk_client = PyJWKClient(jwks_url())
        _jwk_tenant = tid
    return _jwk_client


def validate_access_token(token: str) -> Dict[str, Any]:
    if not tenant_id():
        raise ValueError("Entra tenant not configured")

    signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
    audiences = api_audiences()
    last_error: Exception | None = None

    for audience in audiences:
        try:
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=audience,
                issuer=issuer(),
                options={"require": ["exp", "iat", "sub"]},
                leeway=60,
            )
            if claims.get("tid") and str(claims["tid"]) != tenant_id():
                raise jwt.InvalidIssuerError("Token tenant mismatch")
            return claims
        except jwt.PyJWTError as exc:
            last_error = exc
            continue

    if last_error:
        raise last_error
    raise jwt.InvalidAudienceError("No valid audience configured")
