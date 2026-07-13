from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import get_db
from models import Order, OrderItem, Product, Client, Promo
from schemas import OrderCreate, OrderOut, OrderStatusUpdate
from routers.deps import get_current_client, require_admin
from typing import List

router = APIRouter(prefix="/orders", tags=["orders"])

def calc_discounted_price(price: float, product_id: int, promos: list) -> float:
    for promo in promos:
        if promo.is_active and promo.discount and product_id in (promo.product_ids or []):
            return round(price * (1 - promo.discount / 100), 2)
    return price

@router.post("", response_model=OrderOut)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    client: Client = Depends(get_current_client)
):
    promos_result = await db.execute(select(Promo).where(Promo.is_active == True))
    promos = promos_result.scalars().all()

    items = []
    total = 0.0
    for item_in in data.items:
        p_result = await db.execute(select(Product).where(Product.id == item_in.product_id, Product.is_active == True))
        product = p_result.scalar_one_or_none()
        if not product:
            raise HTTPException(400, f"Mahsulot #{item_in.product_id} topilmadi")
        dp = calc_discounted_price(product.price, product.id, promos)
        sub = dp * item_in.qty
        total += sub
        items.append(OrderItem(
            product_id=product.id,
            qty=item_in.qty,
            unit_price=product.price,
            discounted_price=dp,
            sub_total=sub
        ))

    order = Order(client_id=client.id, total=total, note=data.note)
    db.add(order)
    await db.flush()
    for item in items:
        item.order_id = order.id
        db.add(item)

    # Update accumulated
    client.accumulated = (client.accumulated or 0) + total
    await db.commit()

    result = await db.execute(
        select(Order).options(
            selectinload(Order.client),
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(Order.id == order.id)
    )
    return result.scalar_one()

@router.get("/my", response_model=List[OrderOut])
async def my_orders(db: AsyncSession = Depends(get_db), client: Client = Depends(get_current_client)):
    result = await db.execute(
        select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(Order.client_id == client.id).order_by(Order.created_at.desc())
    )
    return result.scalars().all()

@router.get("", response_model=List[OrderOut])
async def all_orders(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin)
):
    q = select(Order).options(
        selectinload(Order.client),
        selectinload(Order.items).selectinload(OrderItem.product)
    ).order_by(Order.created_at.desc())
    if status:
        q = q.where(Order.status == status)
    result = await db.execute(q)
    return result.scalars().all()

@router.patch("/{order_id}/status")
async def update_status(order_id: int, data: OrderStatusUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Topilmadi")
    allowed = ["new", "accepted", "delivered", "paid"]
    if data.status not in allowed:
        raise HTTPException(400, "Noto'g'ri status")
    order.status = data.status
    await db.commit()
    return {"ok": True, "status": data.status}
