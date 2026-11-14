
import sqlite3
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID
from database import DB_NAME, add_user

router = Router()


def is_admin(user_id):
    return user_id == ADMIN_ID and ADMIN_ID != 0


def prepare_database():
    with sqlite3.connect(DB_NAME) as db:
        columns = [
            row[1] for row in
            db.execute("PRAGMA table_info(users)").fetchall()
        ]

        if "daily_limit" not in columns:
            db.execute(
                "ALTER TABLE users ADD COLUMN daily_limit INTEGER DEFAULT 10"
            )


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return

    with sqlite3.connect(DB_NAME) as db:
        users = db.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        requests = db.execute(
            "SELECT SUM(requests) FROM users"
        ).fetchone()[0] or 0

        unlimited = db.execute(
            "SELECT COUNT(*) FROM users WHERE unlimited = 1"
        ).fetchone()[0]

    await message.answer(
        "🕵️ <b>DEPANOV SHERLOCK</b>\n"
        "⚙️ АДМИН-ПАНЕЛЬ\n\n"
        f"👥 Пользователей: {users}\n"
        f"🔎 Запросов: {requests}\n"
        f"♾️ Безлимитных: {unlimited}\n\n"
        "<b>Команды:</b>\n"
        "/unlimited ID — выдать безлимит\n"
        "/limit ID ЧИСЛО — установить лимит"
    )


@router.message(Command("unlimited"))
async def unlimited_user(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /unlimited ID")
        return

    user_id = int(parts[1])
    add_user(user_id)

    with sqlite3.connect(DB_NAME) as db:
        db.execute(
            "UPDATE users SET unlimited = 1 WHERE user_id = ?",
            (user_id,)
        )

    await message.answer(
        f"♾️ Пользователю {user_id} выдан безлимит!"
    )


@router.message(Command("limit"))
async def set_user_limit(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if (
        len(parts) != 3
        or not parts[1].isdigit()
        or not parts[2].isdigit()
    ):
        await message.answer(
            "Использование: /limit ID ЧИСЛО"
        )
        return

    user_id = int(parts[1])
    amount = int(parts[2])

    if amount > 10000:
        await message.answer("Максимальный лимит — 10000.")
        return

    add_user(user_id)

    with sqlite3.connect(DB_NAME) as db:
        db.execute(
            "UPDATE users SET daily_limit = ?, unlimited = 0 "
            "WHERE user_id = ?",
            (amount, user_id)
        )

    await message.answer(
        f"✅ Лимит пользователя {user_id}: {amount} запросов в день."
    )


prepare_database()
  
