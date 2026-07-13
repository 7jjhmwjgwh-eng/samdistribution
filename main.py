from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from config import settings
from routers import auth, products, orders, clients, promos, accounting, inn
from routers.accounting import rewards_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Seed default products if empty
    await seed_default_data()
    yield

async def seed_default_data():
    from database import AsyncSessionLocal
    from models import Product, RewardSettings
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Product))
        if not result.scalars().first():
            defaults = [
                Product(name_uz="MUZY Olcha soki", name_ru="Сок MUZY Вишня", price=8500, unit_uz="quti (12 ta)", unit_ru="ящик (12 шт)", category="Sok"),
                Product(name_uz="MUZY Shaftoli soki", name_ru="Сок MUZY Персик", price=8500, unit_uz="quti (12 ta)", unit_ru="ящик (12 шт)", category="Sok"),
                Product(name_uz="MUZY Olma soki", name_ru="Сок MUZY Яблоко", price=8500, unit_uz="quti (12 ta)", unit_ru="ящик (12 шт)", category="Sok"),
                Product(name_uz="MUZY Uzum soki", name_ru="Сок MUZY Виноград", price=8500, unit_uz="quti (12 ta)", unit_ru="ящик (12 шт)", category="Sok"),
                Product(name_uz="MUZY Qora choy", name_ru="Чай MUZY Чёрный", price=12000, unit_uz="quti (24 ta)", unit_ru="упаковка (24 шт)", category="Choy"),
                Product(name_uz="MUZY Yashil choy", name_ru="Чай MUZY Зелёный", price=12000, unit_uz="quti (24 ta)", unit_ru="упаковка (24 шт)", category="Choy"),
                Product(name_uz="MUZY Limonli choy", name_ru="Чай MUZY Лимон", price=12000, unit_uz="quti (24 ta)", unit_ru="упаковка (24 шт)", category="Choy"),
                Product(name_uz="MUZY Nanali choy", name_ru="Чай MUZY Мята", price=12000, unit_uz="quti (24 ta)", unit_ru="упаковка (24 шт)", category="Choy"),
            ]
            for p in defaults:
                db.add(p)
            await db.commit()

        rr = await db.execute(select(RewardSettings))
        if not rr.scalar_one_or_none():
            db.add(RewardSettings())
            await db.commit()

app = FastAPI(
    title="SAM Distribution API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        settings.ADMIN_URL,
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(clients.router)
app.include_router(promos.router)
app.include_router(accounting.router)
app.include_router(rewards_router)
app.include_router(inn.router)

@app.get("/")
async def root():
    return {"status": "SAM Distribution API running 🚀"}

@app.get("/health")
async def health():
    return {"ok": True}
