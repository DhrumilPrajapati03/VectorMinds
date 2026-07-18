from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/api/analyze")
async def analyze():
    return JSONResponse(status_code=501, content={"detail": "Not Implemented"})
