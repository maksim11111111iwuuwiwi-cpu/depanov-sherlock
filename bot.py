
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, ADMIN_ID, BOT_NAME
from database import (
    init_db,
    add_user,
    use_request,
    get_stats
)
from search import format_results

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔎 Поиск по нику", callback_data="search")
    kb.button(text="👤 Мой профиль", callback_data="profile")
    kb.adjust(1)
    return kb.as_markup()


@dp.message(Command("start"))
async def start(message: Message):
    add_user(
        message.from_user.id,
        message.from_user.username
    )

    await message.answer(
        f"🕵️ <b>{BOT_NAME}</b>\n\n"
        "Добро пожаловать!\n"
        "Выбери действие:",
        reply_markup=menu(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "search")
async def search_button(call: CallbackQuery):
    await call.message.answer(
        "🔎 Отправь публичный username для поиска."
    )
    await call.answer()


@dp.message(Command("profile"))
async def profile(message: Message):
    await message.answer(
        f"👤 Твой Telegram ID: "
        f"<code>{message.from_user.id}</code>",
        parse_mode="HTML"
    )


@dp.message(F.text.startswith("@"))
async def username_search(message: Message):
    user_id = message.from_user.id

    if not use_request(user_id):
        await message.answer(
            "⛔ Лимит запросов исчерпан."
        )
        return

    result = format_results(message.text)

    await message.answer(
        result or "❌ Некорректный username.",
        parse_mode="HTML"
    )


@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID or ADMIN_ID == 0:
        return

    users, requests = get_stats()

    await message.answer(
        "⚙️ <b>DEPANOV SHERLOCK — ADMIN</b>\n\n"
        f"👥 Пользователей: {users}\n"
        f"🔎 Запросов: {requests}",
        parse_mode="HTML"
    )


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан!")

    init_db()
    print("DEPANOV SHERLOCK запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
