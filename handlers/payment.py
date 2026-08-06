from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from states import TolovForm
from keyboards import filial_kb, admin_payment_kb
from database import get_user, create_payment, get_payment, set_payment_status, decrease_debt
from config import FILIALS, ADMIN_GROUP_ID

router = Router()


@router.message(Command("tolov"))
async def start_tolov(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user or user["status"] != "tasdiqlangan":
        await message.answer("To'lov qilish uchun avval arizangiz tasdiqlangan bo'lishi kerak. /ariza")
        return
    await message.answer(
        f"💰 Joriy qarzdorligingiz: {user['debt']:,} so'm\n\n"
        "To'lov qilmoqchi bo'lgan filialni tanlang:",
        reply_markup=filial_kb()
    )
    await state.set_state(TolovForm.choosing_filial)
