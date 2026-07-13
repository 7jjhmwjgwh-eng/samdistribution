from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    inn = Column(String(20), unique=True, index=True)
    company_name = Column(String(200))
    owner_name = Column(String(200))
    phone = Column(String(20), unique=True, index=True)
    address = Column(String(500))
    password_hash = Column(String(200))
    accumulated = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    orders = relationship("Order", back_populates="client")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name_uz = Column(String(200))
    name_ru = Column(String(200))
    price = Column(Float)
    unit_uz = Column(String(100))
    unit_ru = Column(String(100))
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    total = Column(Float)
    note = Column(Text, nullable=True)
    status = Column(String(20), default="new")  # new/accepted/delivered/paid
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Integer)
    unit_price = Column(Float)
    discounted_price = Column(Float)
    sub_total = Column(Float)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Promo(Base):
    __tablename__ = "promos"
    id = Column(Integer, primary_key=True, index=True)
    title_uz = Column(String(200))
    title_ru = Column(String(200))
    desc_uz = Column(Text)
    desc_ru = Column(Text)
    color = Column(String(20), default="#ef4444")
    discount = Column(Float, nullable=True)
    product_ids = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), index=True)
    code = Column(String(6))
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RewardSettings(Base):
    __tablename__ = "reward_settings"
    id = Column(Integer, primary_key=True, index=True)
    target_mln = Column(Float, default=100.0)
    name_uz = Column(String(200), default="Muzlatgich, konditsioner yoki televizor")
    name_ru = Column(String(200), default="Холодильник, кондиционер или телевизор")
