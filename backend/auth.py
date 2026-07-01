import os
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
# Endpoint geral da Microsoft — cobre tokens do Graph e de qualquer tenant
JWKS_URL = "https://login.microsoftonline.com/common/discovery/v2.0/keys"

bearer_scheme = HTTPBearer()

def _get_jwks() -> dict:
    """Busca as chaves públicas do Azure (sem cache para garantir chaves atualizadas)."""
    response = httpx.get(JWKS_URL, timeout=10)
    response.raise_for_status()
    return response.json()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    """
    Valida o Bearer token JWT emitido pelo Azure AD.
    Retorna o payload decodificado com os dados do usuário.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwks = _get_jwks()
        # Decodifica sem verificar para inspecionar o header e claims
        unverified = jwt.get_unverified_claims(token)
        unverified_header = jwt.get_unverified_header(token)
        print(f"[AUTH DEBUG] token iss: {unverified.get('iss')}")
        print(f"[AUTH DEBUG] token aud: {unverified.get('aud')}")
        print(f"[AUTH DEBUG] token tid: {unverified.get('tid')}")
        print(f"[AUTH DEBUG] token alg: {unverified_header.get('alg')}")
        print(f"[AUTH DEBUG] token kid: {unverified_header.get('kid')}")
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={
                "verify_exp": True,
                "verify_aud": False
            }
        )
        # Garante que o token é do tenant correto
        token_tenant = payload.get("tid")
        if token_tenant != TENANT_ID:
            raise credentials_exception

        user_id: str = payload.get("preferred_username") or payload.get("upn")
        if not user_id:
            raise credentials_exception
        return {"user_id": user_id, "name": payload.get("name", ""), "payload": payload}
    except JWTError as e:
        print(f"[AUTH ERROR] JWTError: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"[AUTH ERROR] Unexpected: {e}")
        raise credentials_exception
