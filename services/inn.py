import httpx

async def lookup_inn(inn: str) -> dict:
    """
    Query Uzbekistan tax service to get company name by INN.
    Uses my.gov.uz / soliq.uz public API.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            # Primary: soliq.uz open API
            r = await client.get(
                f"https://soliq.uz/api/taxpayer-info",
                params={"tin": inn},
                headers={"Accept": "application/json"}
            )
            if r.status_code == 200:
                data = r.json()
                name = data.get("name") or data.get("shortName") or data.get("fullName")
                if name:
                    return {"inn": inn, "company_name": name, "found": True}
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            # Fallback: my.gov.uz
            r = await client.post(
                "https://my.gov.uz/api/taxpayer",
                json={"tin": inn},
                headers={"Content-Type": "application/json"}
            )
            if r.status_code == 200:
                data = r.json()
                name = (
                    data.get("nameShort")
                    or data.get("name")
                    or data.get("organizationName")
                )
                if name:
                    return {"inn": inn, "company_name": name, "found": True}
    except Exception:
        pass

    return {"inn": inn, "company_name": "", "found": False}
