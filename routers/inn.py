from fastapi import APIRouter
from schemas import INNResponse
from services.inn import lookup_inn

router = APIRouter(prefix="/inn", tags=["inn"])

@router.get("/{inn}", response_model=INNResponse)
async def get_inn(inn: str):
    return await lookup_inn(inn)
