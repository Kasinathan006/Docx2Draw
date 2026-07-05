"""
Authentication (guide §5.1 core/auth.py).

Verifies Supabase-issued JWTs (HS256, audience "authenticated"). When no
`SUPABASE_JWT_SECRET` is configured the app runs in open mode and every request
is treated as an anonymous user, so the API is fully usable without auth.
"""
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from ..config import settings
from .exceptions import AuthError

_bearer = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    id: str
    email: Optional[str] = None
    authenticated: bool = False


ANONYMOUS = CurrentUser(id="anonymous", email=None, authenticated=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> CurrentUser:
    """FastAPI dependency returning the authenticated user (or anonymous)."""
    if not settings.auth_enabled:
        return ANONYMOUS

    if credentials is None:
        raise AuthError("Missing bearer token")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as exc:  # invalid signature / expired / wrong audience
        raise AuthError(f"Invalid authentication token: {exc}") from exc

    sub = payload.get("sub")
    if not sub:
        raise AuthError("Token missing subject claim")
    return CurrentUser(id=sub, email=payload.get("email"), authenticated=True)
