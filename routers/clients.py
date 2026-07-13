from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Client
from schemas import ClientOut
from routers.deps import get_current_client, require_admin
from typing import List

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/me", response_model=ClientOut)
async def get_me(client: Client = Depends(get_current_client)):
    return client

@router.get("", response_model=List[ClientOut])
async def get_all_clients(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Client).order_by(Client.created_at.desc()))
    return result.scalars().all()

@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Topilmadi")
    return c

@router.patch("/{client_id}/toggle")
async def toggle_client(client_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Topilmadi")
    c.is_active = not c.is_active
    await db.commit()
    return {"ok": True, "is_active": c.is_active}
