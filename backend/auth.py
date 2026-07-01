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
JWKS_URL = "https://login.microsoftonline.com/common/discovery/v2.0/keys"

bearer_scheme = HTTPBearer()

# PyJWKClient faz cache automático das chaves e busca a certa pelo kid
jwks_client = PyJWKClient(JWKS_URL)

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
        # Busca a chave pública correta pelo kid do token
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False}  # Graph token tem aud diferente
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
