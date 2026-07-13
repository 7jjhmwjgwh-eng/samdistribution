from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ── AUTH ──────────────────────────────────────────────────────────────────────
class SendOTPRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    code: str

class RegisterRequest(BaseModel):
    inn: str
    company_name: str
    owner_name: str
    phone: str
    address: str
    password: str

class LoginRequest(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    client_id: Optional[int] = None

class AdminLoginRequest(BaseModel):
    phone: str
    password: str

# ── INN ───────────────────────────────────────────────────────────────────────
class INNResponse(BaseModel):
    inn: str
    company_name: str
    found: bool

# ── CLIENT ───────────────────────────────────────────────────────────────────
class ClientOut(BaseModel):
    id: int
    inn: str
    company_name: str
    owner_name: str
    phone: str
    address: str
    accumulated: float
    is_active: bool
    created_at: datetime
    class Config: from_attributes = True

# ── PRODUCT ───────────────────────────────────────────────────────────────────
class ProductCreate(BaseModel):
    name_uz: str
    name_ru: str
    price: float
    unit_uz: str
    unit_ru: str
    category: str

class ProductUpdate(BaseModel):
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    price: Optional[float] = None
    unit_uz: Optional[str] = None
    unit_ru: Optional[str] = None
    category: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name_uz: str
    name_ru: str
    price: float
    unit_uz: str
    unit_ru: str
    category: str
    is_active: bool
    class Config: from_attributes = True

# ── ORDER ─────────────────────────────────────────────────────────────────────
class OrderItemIn(BaseModel):
    product_id: int
    qty: int

class OrderCreate(BaseModel):
    items: List[OrderItemIn]
    note: Optional[str] = None

class OrderItemOut(BaseModel):
    product_id: int
    qty: int
    unit_price: float
    discounted_price: float
    sub_total: float
    product: Optional[ProductOut] = None
    class Config: from_attributes = True

class OrderOut(BaseModel):
    id: int
    client_id: int
    total: float
    note: Optional[str]
    status: str
    created_at: datetime
    client: Optional[ClientOut] = None
    items: List[OrderItemOut] = []
    class Config: from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str

# ── PROMO ─────────────────────────────────────────────────────────────────────
class PromoCreate(BaseModel):
    title_uz: str
    title_ru: str
    desc_uz: str
    desc_ru: str
    color: str = "#ef4444"
    discount: Optional[float] = None
    product_ids: List[int] = []

class PromoOut(BaseModel):
    id: int
    title_uz: str
    title_ru: str
    desc_uz: str
    desc_ru: str
    color: str
    discount: Optional[float]
    product_ids: List[int]
    is_active: bool
    class Config: from_attributes = True

class PromoToggle(BaseModel):
    is_active: bool

# ── REWARD ────────────────────────────────────────────────────────────────────
class RewardUpdate(BaseModel):
    target_mln: float
    name_uz: str
    name_ru: str

class RewardOut(BaseModel):
    id: int
    target_mln: float
    name_uz: str
    name_ru: str
    class Config: from_attributes = True

# ── ACCOUNTING ────────────────────────────────────────────────────────────────
class AccountingStats(BaseModel):
    total_revenue: float
    paid_revenue: float
    pending_revenue: float
    orders_count: int
    clients_count: int
    new_orders_count: int
