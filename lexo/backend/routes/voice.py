from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/api/voice")
async def voice():
    return JSONResponse(status_code=501, content={"detail": "Not Implemented"})
