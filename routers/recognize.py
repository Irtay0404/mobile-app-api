from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.openai_service import recognize_from_image

router = APIRouter(prefix="/recognize", tags=["recognize"])


class RecognizeRequest(BaseModel):
    image_base64: str  # base64-encoded JPEG/PNG


@router.post("")
async def recognize(req: RecognizeRequest):
    if not req.image_base64:
        raise HTTPException(400, "image_base64 is required")
    try:
        result = await recognize_from_image(req.image_base64)
        return result
    except Exception as e:
        raise HTTPException(500, f"Recognition failed: {e}")