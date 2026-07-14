from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product
from schemas import ProductCreate, ProductUpdate, ProductOut
from routers.deps import require_admin
from typing import List

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active == True).all()

@router.post("", response_model=ProductOut)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = Product(**data.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.put("/{pid}", response_model=ProductOut)
def update_product(pid: int, data: ProductUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p: raise HTTPException(404, "Topilmadi")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

@router.delete("/{pid}")
def delete_product(pid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p: raise HTTPException(404, "Topilmadi")
    p.is_active = False; db.commit()
    return {"ok": True}
