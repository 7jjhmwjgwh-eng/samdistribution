from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Client
from schemas import ClientOut
from routers.deps import get_current_client, require_admin
from typing import List

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/me", response_model=ClientOut)
def get_me(client: Client = Depends(get_current_client)):
    return client

@router.get("", response_model=List[ClientOut])
def get_all(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Client).order_by(Client.created_at.desc()).all()

@router.get("/{cid}", response_model=ClientOut)
def get_one(cid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    c = db.query(Client).filter(Client.id == cid).first()
    if not c: raise HTTPException(404, "Topilmadi")
    return c

@router.patch("/{cid}/toggle")
def toggle(cid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    c = db.query(Client).filter(Client.id == cid).first()
    if not c: raise HTTPException(404, "Topilmadi")
    c.is_active = not c.is_active; db.commit()
    return {"ok": True, "is_active": c.is_active}
