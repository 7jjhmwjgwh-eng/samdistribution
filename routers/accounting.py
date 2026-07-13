from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Order, Client, RewardSettings
from schemas import AccountingStats, RewardUpdate, RewardOut
from routers.deps import require_admin

router = APIRouter(prefix="/accounting", tags=["accounting"])
rewards_router = APIRouter(prefix="/rewards", tags=["rewards"])

@router.get("/stats", response_model=AccountingStats)
async def get_stats(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    orders_result = await db.execute(select(Order))
    orders = orders_result.scalars().all()
    clients_result = await db.execute(select(func.count(Client.id)))
    clients_count = clients_result.scalar()

    total = sum(o.total for o in orders)
    paid = sum(o.total for o in orders if o.status == "paid")
    pending = sum(o.total for o in orders if o.status != "paid")
    new_count = sum(1 for o in orders if o.status == "new")

    return AccountingStats(
        total_revenue=total,
        paid_revenue=paid,
        pending_revenue=pending,
        orders_count=len(orders),
        clients_count=clients_count or 0,
        new_orders_count=new_count,
    )

@rewards_router.get("", response_model=RewardOut)
async def get_reward(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RewardSettings))
    r = result.scalar_one_or_none()
    if not r:
        r = RewardSettings()
        db.add(r)
        await db.commit()
        await db.refresh(r)
    return r

@rewards_router.put("", response_model=RewardOut)
async def update_reward(data: RewardUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(RewardSettings))
    r = result.scalar_one_or_none()
    if not r:
        r = RewardSettings()
        db.add(r)
    r.target_mln = data.target_mln
    r.name_uz = data.name_uz
    r.name_ru = data.name_ru
    await db.commit()
    await db.refresh(r)
    return r
