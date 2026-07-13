import httpx
import random
from config import settings

ESKIZ_BASE = "https://notify.eskiz.uz/api"
_token_cache = {"token": None}

async def get_eskiz_token() -> str:
    if _token_cache["token"]:
        return _token_cache["token"]
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ESKIZ_BASE}/auth/login", data={
            "email": settings.ESKIZ_EMAIL,
            "password": settings.ESKIZ_PASSWORD
        })
        data = r.json()
        token = data.get("data", {}).get("token", "")
        _token_cache["token"] = token
        return token

async def send_sms(phone: str, message: str) -> bool:
    # Remove + from phone
    phone_clean = phone.replace("+", "")
    try:
        token = await get_eskiz_token()
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{ESKIZ_BASE}/message/sms/send",
                data={
                    "mobile_phone": phone_clean,
                    "message": message,
                    "from": settings.ESKIZ_FROM,
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            result = r.json()
            if result.get("status") == "waiting":
                return True
            # Token expired — refresh
            _token_cache["token"] = None
            token = await get_eskiz_token()
            r2 = await client.post(
                f"{ESKIZ_BASE}/message/sms/send",
                data={
                    "mobile_phone": phone_clean,
                    "message": message,
                    "from": settings.ESKIZ_FROM,
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            return r2.json().get("status") == "waiting"
    except Exception as e:
        print(f"SMS error: {e}")
        return False

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

async def send_otp(phone: str, code: str) -> bool:
    message = f"SAM Distribution tasdiqlash kodi: {code}\nKodni hech kimga bermang!"
    return await send_sms(phone, message)
