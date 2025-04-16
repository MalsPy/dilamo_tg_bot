from aiohttp import web
import hashlib
import os
from aiogram import Bot
from database.engine import session_maker
from database.orm_query import orm_get_user_carts, orm_delete_from_cart

BOT_TOKEN = os.getenv("TOKEN")
SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "F91D8F69C042267444B74CC0B3C747757EB0E065")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "-1001234567890"))  # Замени на реальный ID

async def click_webhook(request):
    data = await request.post()

    try:
        click_trans_id = data["click_trans_id"]
        merchant_trans_id = data["merchant_trans_id"]
        sign = data["sign_string"]
    except KeyError:
        return web.json_response({"error": -8, "error_note": "Missing parameters"})

    control_string = f"{click_trans_id}{data['service_id']}{merchant_trans_id}{SECRET_KEY}"
    expected_sign = hashlib.md5(control_string.encode()).hexdigest()

    if expected_sign != sign:
        return web.json_response({"error": -1, "error_note": "Invalid sign"})

    user_id = int(merchant_trans_id)
    bot = Bot(token=BOT_TOKEN)
    async with session_maker() as session:
        carts = await orm_get_user_carts(session, user_id)
        if not carts:
            return web.json_response({"error": -2, "error_note": "Cart empty"})

        total = sum(float(c.product.price) * c.quantity for c in carts)
        text = (
            f"💸 Новый заказ!\n👤 <code>{user_id}</code>\n\n"
            + "\n".join([f"— {c.product.name} x{c.quantity}" for c in carts])
            + f"\n\n💰 Итого: {total} сум"
        )

        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        await bot.send_message(chat_id=user_id, text="✅ Оплата прошла успешно! Менеджер скоро с вами свяжется.")

        for c in carts:
            await orm_delete_from_cart(session, user_id, c.product_id)
        await session.commit()

    return web.json_response({"error": 0, "error_note": "Success"})
