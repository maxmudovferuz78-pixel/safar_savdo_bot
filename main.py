import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from database import init_db, close_db
from handlers import registration, debt, payment

# Windows'da asyncpg standart Proactor event loop bilan ba'zan
# "connection was closed in the middle of operation" xatosini beradi.
# Shuning uchun Windows'da Selector event loop'ga o'tkazamiz.
from config import BOT_TOKEN

print(BOT_TOKEN)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(registration.router)
dp.include_router(debt.router)
dp.include_router(payment.router)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Assalomu alaykum! 👋\nSafar Savdo botiga xush kelibsiz.\n\n"
        "📋 /ariza — nasiyaga ariza topshirish\n"
        "💰 /qarz — qarzdorligingizni tekshirish\n"
        "💳 /tolov — filialga to'lov qilish"
    )


async def main():
    await init_db()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())