from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Promo
from schemas import PromoCreate, PromoOut, PromoToggle
from routers.deps import require_admin
from typing import List

router = APIRouter(prefix="/promos", tags=["promos"])

@router.get("", response_model=List[PromoOut])
async def get_promos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Promo).order_by(Promo.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=PromoOut)
async def create_promo(data: PromoCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    p = Promo(**data.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p

@router.patch("/{promo_id}/toggle", response_model=PromoOut)
async def toggle_promo(promo_id: int, data: PromoToggle, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Promo).where(Promo.id == promo_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Topilmadi")
    p.is_active = data.is_active
    await db.commit()
    await db.refresh(p)
    return p

@router.delete("/{promo_id}")
async def delete_promo(promo_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Promo).where(Promo.id == promo_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Topilmadi")
    await db.delete(p)
    await db.commit()
    return {"ok": True}
