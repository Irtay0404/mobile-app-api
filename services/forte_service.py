import os
import httpx
from pydantic import BaseModel

FORTE_BASE_URL = os.getenv("FORTE_BASE_URL", "https://sandbox.forte.kz/api/v1")
FORTE_API_KEY  = os.getenv("FORTE_API_KEY", "")
FORTE_MERCHANT = os.getenv("FORTE_MERCHANT_ID", "")


class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    currency: str = "KZT"
    card_number: str
    description: str = "Cashierless payment"


async def process_payment(req: PaymentRequest) -> dict:
    """
    Отправляет платёж в симулятор Forte Bank.
    Замените тело запроса под реальный формат вашего симулятора.
    """
    headers = {
        "Authorization": f"Bearer {FORTE_API_KEY}",
        "Content-Type": "application/json",
        "X-Merchant-Id": FORTE_MERCHANT,
    }

    payload = {
        "order_id":    req.order_id,
        "amount":      req.amount,
        "currency":    req.currency,
        "card_number": req.card_number,
        "description": req.description,
        "merchant_id": FORTE_MERCHANT,
    }

    async with httpx.AsyncClient(timeout=30) as http:
        resp = await http.post(
            f"{FORTE_BASE_URL}/payments",
            json=payload,
            headers=headers,
        )

    if resp.status_code in (200, 201):
        return {"status": "success", "data": resp.json()}
    else:
        return {"status": "error", "code": resp.status_code, "detail": resp.text}