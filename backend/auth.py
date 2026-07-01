import os
import httpx
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")

# Tokens com iss "https://sts.windows.net/..." são v1 — usam endpoint sem /v2.0
JWKS_URL_V1 = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/keys"
JWKS_URL_V2 = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

bearer_scheme = HTTPBearer()
jwks_client_v1 = PyJWKClient(JWKS_URL_V1)
jwks_client_v2 = PyJWKClient(JWKS_URL_V2)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Tenta v1 primeiro (iss = sts.windows.net), depois v2
        signing_key = None
        for client in [jwks_client_v1, jwks_client_v2]:
            try:
                signing_key = client.get_signing_key_from_jwt(token)
                break
            except Exception:
                continue

        if not signing_key:
            raise credentials_exception

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )

        # Valida que o token pertence ao tenant correto
        if payload.get("tid") != TENANT_ID:
            raise credentials_exception

        user_id: str = payload.get("preferred_username") or payload.get("upn")
        if not user_id:
            raise credentials_exception

        return {"user_id": user_id, "name": payload.get("name", ""), "payload": payload}

    except Exception as e:
        print(f"[AUTH ERROR] {type(e).__name__}: {e}")
        raise credentials_exception
