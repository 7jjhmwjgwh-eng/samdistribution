from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import Client, OTPCode
from schemas import SendOTPRequest, VerifyOTPRequest, RegisterRequest, LoginRequest, TokenResponse
from services.eskiz import send_otp, generate_otp
from services.auth import hash_password, verify_password, create_token
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/send-otp")
def send_otp_endpoint(req: SendOTPRequest, db: Session = Depends(get_db)):
    db.query(OTPCode).filter(OTPCode.phone == req.phone).delete()
    db.commit()
    code = generate_otp()
    db.add(OTPCode(phone=req.phone, code=code))
    db.commit()
    import asyncio
    try:
        sent = asyncio.run(send_otp(req.phone, code))
    except:
        sent = False
    if not sent:
        return {"message": "SMS yuborilmadi (Eskiz sozlanmagan)", "dev_code": code}
    return {"message": "SMS yuborildi"}

@router.post("/verify-otp")
def verify_otp_endpoint(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    otp = db.query(OTPCode).filter(
        OTPCode.phone == req.phone,
        OTPCode.code == req.code,
        OTPCode.is_used == False,
        OTPCode.created_at >= datetime.utcnow() - timedelta(minutes=10)
    ).order_by(OTPCode.created_at.desc()).first()
    if not otp:
        raise HTTPException(400, "Noto'g'ri yoki muddati o'tgan kod")
    otp.is_used = True
    db.commit()
    return {"verified": True}

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Client).filter(Client.phone == req.phone).first():
        raise HTTPException(400, "Bu raqam allaqachon ro'yxatdan o'tgan")
    if db.query(Client).filter(Client.inn == req.inn).first():
        raise HTTPException(400, "Bu INN allaqachon ro'yxatdan o'tgan")
    client = Client(
        inn=req.inn, company_name=req.company_name, owner_name=req.owner_name,
        phone=req.phone, address=req.address, password_hash=hash_password(req.password)
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    token = create_token({"sub": str(client.id), "role": "client"})
    return TokenResponse(access_token=token, role="client", client_id=client.id)

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    if req.phone == settings.ADMIN_PHONE and req.password == settings.ADMIN_PASSWORD:
        token = create_token({"sub": "admin", "role": "admin"})
        return TokenResponse(access_token=token, role="admin")
    client = db.query(Client).filter(Client.phone == req.phone).first()
    if not client or not verify_password(req.password, client.password_hash):
        raise HTTPException(401, "Telefon yoki parol noto'g'ri")
    if not client.is_active:
        raise HTTPException(403, "Hisobingiz bloklangan")
    token = create_token({"sub": str(client.id), "role": "client"})
    return TokenResponse(access_token=token, role="client", client_id=client.id)
