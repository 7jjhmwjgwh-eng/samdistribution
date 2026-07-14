from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import Client
from services.auth import decode_token

bearer = HTTPBearer()

def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> Client:
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "client":
        raise HTTPException(status_code=401, detail="Token noto'g'ri")
    client = db.query(Client).filter(Client.id == int(payload["sub"])).first()
    if not client:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return client

def require_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin huquqi kerak")
    return payload
