from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_add_to_cart,
    orm_add_user,
    orm_get_user_carts,
    orm_delete_from_cart,
)

from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from kbds.inline import MenuCallBack, get_callback_btns

import os


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("🛒 Товар добавлен в корзину.")


async def process_order(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    carts = await orm_get_user_carts(session, user.id)

    if not carts:
        await callback.message.answer("❗ Ваша корзина пуста.")
        await callback.answer()
        return

    total = sum(float(c.product.price) * c.quantity for c in carts)
    summary = "\n".join([f"— {c.product.name} x{c.quantity}" for c in carts])

    admin_text = (
        f"📥 <b>Новый заказ</b>\n"
        f"👤 <b>{user.full_name}</b> (@{user.username or 'без username'} | <code>{user.id}</code>)\n\n"
        f"{summary}\n\n"
        f"💰 Итого: <b>{format(int(total), ',').replace(',', ' ')}</b> сум"
    )

    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    if not ADMIN_CHAT_ID:
        await callback.message.answer("❗ ADMIN_CHAT_ID не указан в .env")
        return

    bot = Bot(token=os.getenv("TOKEN"))
    await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=admin_text, parse_mode="HTML")

    await callback.message.answer(
        "✅ Заказ принят!\n"
        "💬 Администратор скоро свяжется с вами для подтверждения."
    )

    for c in carts:
        await orm_delete_from_cart(session, user.id, c.product_id)
    await session.commit()

    await callback.answer("Спасибо за заказ!")


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return

    elif callback_data.menu_name == "order":
        await process_order(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()
