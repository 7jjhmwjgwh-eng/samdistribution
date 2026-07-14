from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Promo
from schemas import PromoCreate, PromoOut, PromoToggle
from routers.deps import require_admin
from typing import List

router = APIRouter(prefix="/promos", tags=["promos"])

@router.get("", response_model=List[PromoOut])
def get_promos(db: Session = Depends(get_db)):
    return db.query(Promo).order_by(Promo.created_at.desc()).all()

@router.post("", response_model=PromoOut)
def create_promo(data: PromoCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = Promo(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return p

@router.patch("/{pid}/toggle", response_model=PromoOut)
def toggle_promo(pid: int, data: PromoToggle, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = db.query(Promo).filter(Promo.id == pid).first()
    if not p: raise HTTPException(404, "Topilmadi")
    p.is_active = data.is_active; db.commit(); db.refresh(p); return p

@router.delete("/{pid}")
def delete_promo(pid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = db.query(Promo).filter(Promo.id == pid).first()
    if not p: raise HTTPException(404, "Topilmadi")
    db.delete(p); db.commit(); return {"ok": True}
