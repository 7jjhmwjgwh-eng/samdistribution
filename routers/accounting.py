from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Client, RewardSettings
from schemas import AccountingStats, RewardUpdate, RewardOut
from routers.deps import require_admin

router = APIRouter(prefix="/accounting", tags=["accounting"])
rewards_router = APIRouter(prefix="/rewards", tags=["rewards"])

@router.get("/stats", response_model=AccountingStats)
def get_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    orders = db.query(Order).all()
    return AccountingStats(
        total_revenue=sum(o.total for o in orders),
        paid_revenue=sum(o.total for o in orders if o.status=="paid"),
        pending_revenue=sum(o.total for o in orders if o.status!="paid"),
        orders_count=len(orders),
        clients_count=db.query(Client).count(),
        new_orders_count=sum(1 for o in orders if o.status=="new"),
    )

@rewards_router.get("", response_model=RewardOut)
def get_reward(db: Session = Depends(get_db)):
    r = db.query(RewardSettings).first()
    if not r:
        r = RewardSettings(); db.add(r); db.commit(); db.refresh(r)
    return r

@rewards_router.put("", response_model=RewardOut)
def update_reward(data: RewardUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = db.query(RewardSettings).first()
    if not r:
        r = RewardSettings(); db.add(r)
    r.target_mln = data.target_mln; r.name_uz = data.name_uz; r.name_ru = data.name_ru
    db.commit(); db.refresh(r); return r
