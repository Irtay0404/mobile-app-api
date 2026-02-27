from fastapi import APIRouter
from database import get_all_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def get_products():
    """
    Получить список всех товаров.
    
    Возвращает все товары из базы данных, отсортированные по названию.
    """
    products = await get_all_products()
    return {
        "count": len(products),
        "products": products
    }
