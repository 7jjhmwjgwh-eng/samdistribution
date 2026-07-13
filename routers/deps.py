from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Client
from services.auth import decode_token

bearer = HTTPBearer()

async def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
) -> Client:
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "client":
        raise HTTPException(status_code=401, detail="Token noto'g'ri")
    result = await db.execute(select(Client).where(Client.id == int(payload["sub"])))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return client

def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin huquqi kerak")
    return payload
