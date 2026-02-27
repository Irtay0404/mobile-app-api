import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.forte_service import PaymentRequest, process_payment

router = APIRouter(prefix="/checkout", tags=["checkout"])


class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int


class CheckoutRequest(BaseModel):
    items: list[CartItem]
    total: float
    card_number: str


@router.post("")
async def checkout(req: CheckoutRequest):
    order_id = f"ORDER-{uuid.uuid4().hex[:8].upper()}"

    pay_req = PaymentRequest(
        order_id=order_id,
        amount=req.total,
        card_number=req.card_number,
        description=f"Store purchase: {len(req.items)} items",
    )

    result = await process_payment(pay_req)

    return {
        "order_id": order_id,
        "payment": result,
        "items": [i.model_dump() for i in req.items],
        "total": req.total,
    }