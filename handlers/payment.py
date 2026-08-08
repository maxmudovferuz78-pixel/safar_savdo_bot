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


@router.callback_query(TolovForm.choosing_filial, F.data.startswith("filial_"))
async def choose_filial(callback: CallbackQuery, state: FSMContext):
    key = callback.data.replace("filial_", "")
    filial = FILIALS[key]
    await state.update_data(filial_key=key, filial_name=filial["name"])
    await callback.message.edit_text(
        f"🏢 {filial['name']}\n"
        f"💳 Karta raqami: <code>{filial['card']}</code>\n\n"
        f"To'lovni shu kartaga o'tkazgandan so'ng, to'lov summasini kiriting (so'mda):",
        parse_mode="HTML"
    )
    await state.set_state(TolovForm.entering_amount)
    await callback.answer()


@router.message(TolovForm.entering_amount)
async def enter_amount(message: Message, state: FSMContext, bot: Bot):
    cleaned = message.text.replace(" ", "").replace(",", "")
    if not cleaned.isdigit():
        await message.answer("Iltimos, summani faqat raqamda kiriting:")
        return
    amount = int(cleaned)
    data = await state.get_data()

    payment_id = await create_payment(message.from_user.id, data["filial_key"], data["filial_name"], amount)
    await state.clear()

    await message.answer("✅ To'lovingiz qabul qilindi va tekshiruvga yuborildi. Tasdiqlangach chek yuboriladi.")

    await bot.send_message(
        ADMIN_GROUP_ID,
        f"💳 <b>Yangi to'lov</b>\n\n"
        f"👤 User ID: <code>{message.from_user.id}</code>\n"
        f"👤 Username: @{message.from_user.username if message.from_user.username else '-'}\n"
        f"🏢 Filial: {data['filial_name']}\n"
        f"💰 Summa: {amount:,} so'm\n"
        f"🆔 To'lov ID: {payment_id}",
        parse_mode="HTML",
        reply_markup=admin_payment_kb(payment_id)
    )

    @router.callback_query(F.data.startswith("pay_ok_"))
    async def approve_payment(callback: CallbackQuery, bot: Bot):
        payment_id = int(callback.data.replace("pay_ok_", ""))
        payment = await get_payment(payment_id)
        if not payment or payment["status"] != "kutilmoqda":
            await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan.", show_alert=True)
            return

        await set_payment_status(payment_id, "tasdiqlangan")
        new_debt = await decrease_debt(payment["user_id"], payment["amount"])

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Tasdiqlandi")

        chek = (
            f"🧾 <b>CHEK</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🏢 Filial: {payment['filial_name']}\n"
            f"💰 To'langan summa: {payment['amount']:,} so'm\n"
            f"📅 Sana: {payment['created_at']}\n"
            f"💳 Qolgan qarzdorlik: {new_debt:,} so'm\n"
            f"━━━━━━━━━━━━━━\n"
            f"✅ To'lovingiz uchun rahmat!"
        )
        await bot.send_message(payment["user_id"], chek, parse_mode="HTML")

    @router.callback_query(F.data.startswith("pay_no_"))
    async def reject_payment(callback: CallbackQuery, bot: Bot):
        payment_id = int(callback.data.replace("pay_no_", ""))
        payment = await get_payment(payment_id)
        if not payment or payment["status"] != "kutilmoqda":
            await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan.", show_alert=True)
            return
        await set_payment_status(payment_id, "rad etilgan")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Rad etildi")
        await bot.send_message(
            payment["user_id"],
            f"❌ Sizning {payment['amount']:,} so'mlik to'lovingiz tasdiqlanmadi. Iltimos, admin bilan bog'laning."
        )
