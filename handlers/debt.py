from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database import get_user, set_status, set_debt
from config import ADMIN_GROUP_ID

router = Router()


@router.message(Command("qarz"))
async def check_debt(message: Message):
    # Admin guruhida ishlatilsa: /qarz <user_id> <summa> - qarzni belgilash uchun
    if message.chat.id == ADMIN_GROUP_ID:
        parts = message.text.split()
        if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            user_id, amount = int(parts[1]), int(parts[2])
            user = await get_user(user_id)
            if not user:
                await message.reply("Bunday foydalanuvchi topilmadi.")
                return
            await set_debt(user_id, amount)
            await message.reply(f"✅ {user['full_name']} uchun qarz {amount:,} so'm qilib belgilandi.")
            await message.bot.send_message(
                user_id,
                f"Sizga {amount:,} so'm miqdorida nasiya tasdiqlandi.\n"
                f"Joriy qarzdorligingiz: {amount:,} so'm"
            )
        else:
            await message.reply("Foydalanish: /qarz <user_id> <summa>")
        return

    # Oddiy foydalanuvchi o'z qarzini tekshiradi
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Siz hali ariza topshirmagansiz. /ariza buyrug'ini yuboring.")
        return
    if user["status"] != "tasdiqlangan":
        await message.answer(f"Arizangiz holati: {user['status']}.\nHozircha qarzdorlik mavjud emas.")
        return
    await message.answer(f"💰 Sizning joriy qarzdorligingiz: {user['debt']:,} so'm")