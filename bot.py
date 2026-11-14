
import os
import sqlite3
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

db = sqlite3.connect("sherlock.db")
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
""")
db.commit()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔎 Поиск по нику",
                callback_data="username"
            )
        ],
        [
            InlineKeyboardButton(
                text="🌐 Открытые источники",
                callback_data="sources"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 Мой профиль",
                callback_data="profile"
            )
        ]
    ])


@dp.message(Command("start"))
async def start(message: Message):
    db.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?)",
        (message.from_user.id, message.from_user.username)
    )
    db.commit()

    await message.answer(
        "🕵️ <b>DEPANOV SHERLOCK</b>\n\n"
        "Добро пожаловать!\n"
        "Выбери нужный раздел:",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "username")
async def username_search(call: CallbackQuery):
    await call.message.answer(
        "🔎 Отправь публичный username для проверки."
    )
    await call.answer()


@dp.message(F.text.startswith("@"))
async def search_username(message: Message):
    username = message.text.strip().lstrip("@")

    if not username.replace("_", "").isalnum():
        await message.answer("❌ Некорректный username.")
        return

    links = [
        f"https://t.me/{username}",
        f"https://www.instagram.com/{username}/",
        f"https://www.tiktok.com/@{username}",
        f"https://x.com/{username}"
    ]

    result = "🔎 <b>Публичные профили</b>\n\n"

    for link in links:
        result += f"🌐 <a href='{link}'>{link}</a>\n"

    result += "\n<i>Ссылки требуют самостоятельной проверки.</i>"

    await message.answer(result)


@dp.callback_query(F.data == "sources")
async def sources(call: CallbackQuery):
    await call.message.answer(
        "🌐 Здесь будет раздел поиска по открытым источникам."
    )
    await call.answer()


@dp.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    count = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    await call.message.answer(
        f"👤 Твой ID: <code>{call.from_user.id}</code>\n"
        f"👥 Пользователей бота: {count}"
    )
    await call.answer()


@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return

    count = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    await message.answer(
        f"⚙️ <b>Админ-панель</b>\n\n"
        f"👥 Всего пользователей: {count}"
    )


async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не задан!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
      
