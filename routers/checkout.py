import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from services.forte_service import create_order, get_order_status

router = APIRouter(prefix="/checkout", tags=["checkout"])

# ── In-memory хранилище ордеров (для демо достаточно) ─────────────────────────
# { our_order_id: { forte_order_id, forte_password, status, items, total } }
_orders: dict[str, dict] = {}


class CartItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int


class CheckoutRequest(BaseModel):
    items: list[CartItem]
    total: float


# ── 1. Создать ордер и получить HPP-ссылку ────────────────────────────────────
@router.post("/create")
async def create_checkout(req: CheckoutRequest, request: Request):
    our_order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # callback URL — Forte редиректнёт сюда после оплаты
    # На демо это ngrok-адрес нашего бэкенда
    base_url = str(request.base_url).rstrip("/")
    callback_url = f"{base_url}/checkout/callback"

    item_names = ", ".join(i.name for i in req.items[:3])
    description = f"Покупка: {item_names}"

    try:
        forte_data = await create_order(
            amount=req.total,
            description=description,
            redirect_url=f"{callback_url}?our_order_id={our_order_id}",
        )
    except Exception as e:
        raise HTTPException(502, f"Forte error: {e}")

    _orders[our_order_id] = {
        "forte_order_id": forte_data["forte_order_id"],
        "forte_password": forte_data["forte_password"],
        "status":         "pending",   # наш внутренний статус
        "items":          [i.model_dump() for i in req.items],
        "total":          req.total,
    }

    return {
        "our_order_id": our_order_id,
        "hpp_url":      forte_data["hpp_url"],
        "total":        req.total,
    }


# ── 2. Callback от Forte после оплаты ─────────────────────────────────────────
@router.get("/callback", response_class=HTMLResponse)
async def payment_callback(our_order_id: str, ID: int | None = None, STATUS: str | None = None):
    """
    Forte редиректит сюда с параметрами:
      ?our_order_id=ORD-xxx&ID=<forte_id>&STATUS=FullyPaid|Declined
    """
    if our_order_id not in _orders:
        return HTMLResponse("<h1>Order not found</h1>", status_code=404)

    order = _orders[our_order_id]

    if STATUS == "FullyPaid":
        order["status"] = "paid"
    elif STATUS in ("Declined", "Expired", "Cancelled", "Refused"):
        order["status"] = "failed"
    else:
        # Если статус не пришёл — запрашиваем у Forte напрямую
        try:
            forte_status = await get_order_status(
                order["forte_order_id"],
                order["forte_password"],
            )
            order["status"] = "paid" if forte_status == "FullyPaid" else "failed"
        except Exception:
            order["status"] = "failed"

    # Показываем красивую страницу-заглушку (браузер закроют вручную)
    if order["status"] == "paid":
        html = f"""
        <html><body style="font-family:sans-serif;text-align:center;padding:40px;background:#f0fdf4">
        <h1 style="color:#16a34a">✅ Оплата прошла успешно!</h1>
        <p>Заказ: <b>{our_order_id}</b></p>
        <p>Сумма: <b>{order['total']:,.0f} ₸</b></p>
        <p style="color:#666">Вернитесь в приложение</p>
        </body></html>
        """
    else:
        html = f"""
        <html><body style="font-family:sans-serif;text-align:center;padding:40px;background:#fef2f2">
        <h1 style="color:#dc2626">❌ Оплата отклонена</h1>
        <p>Заказ: <b>{our_order_id}</b></p>
        <p style="color:#666">Вернитесь в приложение и попробуйте снова</p>
        </body></html>
        """

    return HTMLResponse(html)


# ── 3. Поллинг статуса из мобильного приложения ───────────────────────────────
@router.get("/status/{our_order_id}")
async def get_status(our_order_id: str):
    if our_order_id not in _orders:
        raise HTTPException(404, "Order not found")

    order = _orders[our_order_id]

    # Если ещё pending — дополнительно спросим Forte (на случай потери callback)
    if order["status"] == "pending":
        try:
            forte_status = await get_order_status(
                order["forte_order_id"],
                order["forte_password"],
            )
            if forte_status == "FullyPaid":
                order["status"] = "paid"
            elif forte_status in ("Declined", "Expired", "Cancelled"):
                order["status"] = "failed"
        except Exception:
            pass  # оставляем pending, приложение попробует ещё раз

    return {
        "our_order_id":    our_order_id,
        "status":          order["status"],   # pending | paid | failed
        "forte_order_id":  order["forte_order_id"],
        "items":           order["items"],
        "total":           order["total"],
    }