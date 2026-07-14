from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings
import re

def fix_url(url: str) -> str:
    url = url.strip().strip('"').strip("'")
    url = re.sub(r'^postgres(ql)?(\+\w+)?://', 'postgresql+psycopg2://', url)
    return url

db_url = fix_url(settings.DATABASE_URL)
engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models import Client, Product, Order, OrderItem, Promo, OTPCode, RewardSettings
    Base.metadata.create_all(bind=engine)
