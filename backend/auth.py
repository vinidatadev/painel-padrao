import os
import httpx
import jwt
from cryptography.x509 import load_der_x509_certificate
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")

# idToken é assinado com chaves do endpoint v2.0
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

bearer_scheme = HTTPBearer()

def _get_public_key(kid: str):
    resp = httpx.get(JWKS_URL, timeout=10)
    resp.raise_for_status()
    keys = resp.json().get("keys", [])
    for key in keys:
        if key.get("kid") == kid:
            x5c = key.get("x5c", [])
            if x5c:
                cert_der = b64decode(x5c[0])
                cert = load_der_x509_certificate(cert_der, default_backend())
                return cert.public_key()
    return None

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
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        public_key = _get_public_key(kid)
        if not public_key:
            print(f"[AUTH ERROR] kid não encontrado: {kid}")
            raise credentials_exception

        # idToken: audience = CLIENT_ID, issuer = v2.0 do tenant
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
        )

        user_id: str = payload.get("preferred_username") or payload.get("email") or payload.get("upn")
        if not user_id:
            raise credentials_exception

        return {"user_id": user_id, "name": payload.get("name", ""), "payload": payload}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH ERROR] {type(e).__name__}: {e}")
        raise credentials_exception
