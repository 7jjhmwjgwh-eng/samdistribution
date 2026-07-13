from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from database import get_db
from models import Client, OTPCode
from schemas import SendOTPRequest, VerifyOTPRequest, RegisterRequest, LoginRequest, TokenResponse, AdminLoginRequest
from services.eskiz import send_otp, generate_otp
from services.auth import hash_password, verify_password, create_token
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/send-otp")
async def send_otp_endpoint(req: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    # Delete old OTPs for this phone
    await db.execute(delete(OTPCode).where(OTPCode.phone == req.phone))
    await db.commit()

    code = generate_otp()
    otp = OTPCode(phone=req.phone, code=code)
    db.add(otp)
    await db.commit()

    sent = await send_otp(req.phone, code)

    # In dev mode — return code if SMS fails
    if not sent:
        return {"message": "SMS not sent (check Eskiz config)", "dev_code": code}

    return {"message": "SMS yuborildi"}

@router.post("/verify-otp")
async def verify_otp_endpoint(req: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OTPCode).where(
            OTPCode.phone == req.phone,
            OTPCode.code == req.code,
            OTPCode.is_used == False,
            OTPCode.created_at >= datetime.utcnow() - timedelta(minutes=10)
        ).order_by(OTPCode.created_at.desc())
    )
    otp = result.scalar_one_or_none()
    if not otp:
        raise HTTPException(status_code=400, detail="Noto'g'ri yoki muddati o'tgan kod")

    otp.is_used = True
    await db.commit()
    return {"verified": True}

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check phone exists
    existing = await db.execute(select(Client).where(Client.phone == req.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu raqam allaqachon ro'yxatdan o'tgan")

    # Check INN exists
    existing_inn = await db.execute(select(Client).where(Client.inn == req.inn))
    if existing_inn.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu INN allaqachon ro'yxatdan o'tgan")

    client = Client(
        inn=req.inn,
        company_name=req.company_name,
        owner_name=req.owner_name,
        phone=req.phone,
        address=req.address,
        password_hash=hash_password(req.password),
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)

    token = create_token({"sub": str(client.id), "role": "client"})
    return TokenResponse(access_token=token, role="client", client_id=client.id)

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Check admin
    if req.phone == settings.ADMIN_PHONE and req.password == settings.ADMIN_PASSWORD:
        token = create_token({"sub": "admin", "role": "admin"})
        return TokenResponse(access_token=token, role="admin")

    result = await db.execute(select(Client).where(Client.phone == req.phone))
    client = result.scalar_one_or_none()
    if not client or not verify_password(req.password, client.password_hash):
        raise HTTPException(status_code=401, detail="Telefon yoki parol noto'g'ri")
    if not client.is_active:
        raise HTTPException(status_code=403, detail="Hisobingiz bloklangan")

    token = create_token({"sub": str(client.id), "role": "client"})
    return TokenResponse(access_token=token, role="client", client_id=client.id)
