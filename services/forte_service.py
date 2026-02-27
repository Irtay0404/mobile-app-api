import os
import httpx
import base64

FORTE_BASE_URL = os.getenv("FORTE_BASE_URL", "http://localhost:8082")
FORTE_LOGIN    = os.getenv("FORTE_LOGIN", "TerminalSys/Login1")
FORTE_PASSWORD = os.getenv("FORTE_PASSWORD", "Password1234")


def _basic_auth_header() -> str:
    credentials = f"{FORTE_LOGIN}:{FORTE_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


async def create_order(amount: float, description: str, redirect_url: str) -> dict:
    """
    Создаёт ордер в Forte и возвращает:
      - order_id   (int64)
      - password   (str)
      - hpp_url    (str) — ссылка для открытия в браузере
    """
    # Forte принимает сумму в тиынах (минимальных единицах).
    # 1 тенге = 100 тиын → умножаем на 100
    amount_tiyn = int(amount * 100)

    payload = {
        "order": {
            "typeRid":       "Order_RID",
            "language":      "ru",
            "amount":        str(amount_tiyn),
            "currency":      "KZT",
            "hppRedirectUrl": redirect_url,
            "description":   description,
            "title":         "Cashierless Store",
        }
    }

    headers = {
        "Authorization": _basic_auth_header(),
        "Content-Type":  "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{FORTE_BASE_URL}/order",
            json=payload,
            headers=headers,
        )

    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Forte create_order failed: {resp.status_code} {resp.text}")

    data = resp.json()
    order = data["order"]

    order_id = order["id"]
    password = order["password"]
    hpp_base = order.get("hppUrl", f"{FORTE_BASE_URL}/flex")

    # Формируем ссылку на платёжную форму
    hpp_url = f"{hpp_base}?id={order_id}&password={password}"

    return {
        "forte_order_id": order_id,
        "forte_password": password,
        "hpp_url":        hpp_url,
        "status":         order.get("status", "Preparing"),
    }


async def get_order_status(forte_order_id: int, password: str) -> str:
    """Возвращает статус ордера: Preparing | FullyPaid | Declined | ..."""
    headers = {"Authorization": _basic_auth_header()}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{FORTE_BASE_URL}/order/{forte_order_id}",
            params={"password": password, "tranDetailLevel": "1"},
            headers=headers,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"Forte get_order failed: {resp.status_code}")

    data = resp.json()

    # Если ордер не найден — Forte возвращает errorCode
    if "errorCode" in data:
        raise RuntimeError(data.get("errorDescription", "Order not found"))

    return data["order"]["status"]