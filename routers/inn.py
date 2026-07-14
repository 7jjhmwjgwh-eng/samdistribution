from fastapi import APIRouter
from schemas import INNResponse
import httpx

router = APIRouter(prefix="/inn", tags=["inn"])

@router.get("/{inn}", response_model=INNResponse)
async def get_inn(inn: str):
    # Try multiple public endpoints for Uzbekistan INN lookup
    inn = inn.strip()
    
    # Method 1: my3.soliq.uz public API
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(
                f"https://my3.soliq.uz/roaming-new/api/v1/taxpayers/{inn}",
                headers={"Accept": "application/json"}
            )
            if r.status_code == 200:
                d = r.json()
                name = d.get("name") or d.get("shortName") or d.get("fullName") or d.get("taxpayerName")
                if name:
                    return {"inn": inn, "company_name": name, "found": True}
    except Exception:
        pass

    # Method 2: cabinet.soliq.uz
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(
                "https://cabinet.soliq.uz/api/v1/taxpayer/find",
                json={"tin": inn},
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            if r.status_code == 200:
                d = r.json()
                name = d.get("name") or d.get("shortName") or d.get("organizationName")
                if name:
                    return {"inn": inn, "company_name": name, "found": True}
    except Exception:
        pass

    # Method 3: faktura.uz public search
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(
                f"https://safe.faktura.uz/api/v1/company/{inn}",
                headers={"Accept": "application/json"}
            )
            if r.status_code == 200:
                d = r.json()
                name = d.get("name") or d.get("shortName")
                if name:
                    return {"inn": inn, "company_name": name, "found": True}
    except Exception:
        pass

    return {"inn": inn, "company_name": "", "found": False}
