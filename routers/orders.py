from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Order, OrderItem, Product, Client, Promo
from schemas import OrderCreate, OrderOut, OrderStatusUpdate
from routers.deps import get_current_client, require_admin
from typing import List, Optional

router = APIRouter(prefix="/orders", tags=["orders"])

def get_discounted(price, pid, promos):
    for p in promos:
        if p.is_active and p.discount and pid in (p.product_ids or []):
            return round(price * (1 - p.discount / 100), 2)
    return price

@router.post("", response_model=OrderOut)
def create_order(data: OrderCreate, db: Session = Depends(get_db), client: Client = Depends(get_current_client)):
    promos = db.query(Promo).filter(Promo.is_active == True).all()
    items, total = [], 0.0
    for item_in in data.items:
        prod = db.query(Product).filter(Product.id == item_in.product_id, Product.is_active == True).first()
        if not prod: raise HTTPException(400, f"Mahsulot #{item_in.product_id} topilmadi")
        dp = get_discounted(prod.price, prod.id, promos)
        sub = dp * item_in.qty; total += sub
        items.append(OrderItem(product_id=prod.id, qty=item_in.qty, unit_price=prod.price, discounted_price=dp, sub_total=sub))
    order = Order(client_id=client.id, total=total, note=data.note)
    db.add(order); db.flush()
    for item in items:
        item.order_id = order.id; db.add(item)
    client.accumulated = (client.accumulated or 0) + total
    db.commit()
    return db.query(Order).options(joinedload(Order.client), joinedload(Order.items).joinedload(OrderItem.product)).filter(Order.id == order.id).first()

@router.get("/my", response_model=List[OrderOut])
def my_orders(db: Session = Depends(get_db), client: Client = Depends(get_current_client)):
    return db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.product)).filter(Order.client_id == client.id).order_by(Order.created_at.desc()).all()

@router.get("", response_model=List[OrderOut])
def all_orders(status: Optional[str] = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    q = db.query(Order).options(joinedload(Order.client), joinedload(Order.items).joinedload(OrderItem.product)).order_by(Order.created_at.desc())
    if status: q = q.filter(Order.status == status)
    return q.all()

@router.patch("/{oid}/status")
def update_status(oid: int, data: OrderStatusUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    order = db.query(Order).filter(Order.id == oid).first()
    if not order: raise HTTPException(404, "Topilmadi")
    if data.status not in ["new","accepted","delivered","paid"]: raise HTTPException(400, "Noto'g'ri status")
    order.status = data.status; db.commit()
    return {"ok": True, "status": data.status}
