from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from states import ArizaForm
from keyboards import family_status_kb, house_type_kb, yes_no_kb, contact_kb, admin_ariza_kb
from database import save_application
from config import ADMIN_GROUP_ID

router = Router()


def calculate_score(data: dict) -> int:
    """
    Excel formulasi asosida ball hisoblash:
    =IF(Daromad>=3000000,20,10)
    +IF(Ish="bor",20,0)
    +IF(Uy="o'z uy",15,0)
    +IF(Tel_yil>=2,10,0)
    +IF(Kafil="ha",20,0)
    Maksimal ball: 85
    """
    score = 20 if data["income"] >= 3_000_000 else 10
    score += 20 if data["workplace"].strip().lower() not in ("", "yo'q", "yoq") else 0
    score += 15 if data["house_type"] == "O'z uy" else 0
    score += 10 if data["phone_years"] >= 2 else 0
    score += 20 if data["guarantor"] == "Ha" else 0
    return score


@router.message(Command("ariza"))
async def start_ariza(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! 👋\nSafar Savdoga xush kelibsiz\n\n"
        "Ism familiyangizni kiriting:"
    )
    await state.set_state(ArizaForm.full_name)


@router.message(ArizaForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Tug'ilgan yilingizni kiriting (masalan: 1995):")
    await state.set_state(ArizaForm.birth_year)


@router.message(ArizaForm.birth_year)
async def get_birth_year(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, yilni raqamda kiriting (masalan: 1995):")
        return
    await state.update_data(birth_year=int(message.text))
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=contact_kb())
    await state.set_state(ArizaForm.phone)


@router.message(ArizaForm.phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Qayerda ishlaysiz?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ArizaForm.workplace)


@router.message(ArizaForm.phone)
async def get_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Qayerda ishlaysiz?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ArizaForm.workplace)


@router.message(ArizaForm.workplace)
async def get_workplace(message: Message, state: FSMContext):
    await state.update_data(workplace=message.text)
    await message.answer("Oylik daromadingiz qancha? (so'mda, faqat raqam yozing):")
    await state.set_state(ArizaForm.income)


@router.message(ArizaForm.income)
async def get_income(message: Message, state: FSMContext):
    cleaned = message.text.replace(" ", "").replace(",", "")
    if not cleaned.isdigit():
        await message.answer("Iltimos, daromadni faqat raqamda yozing (masalan: 3000000):")
        return
    await state.update_data(income=int(cleaned))
    await message.answer("Oilaviy holatingiz:", reply_markup=family_status_kb())
    await state.set_state(ArizaForm.family_status)


@router.callback_query(ArizaForm.family_status, F.data.startswith("fam_"))
async def get_family_status(callback: CallbackQuery, state: FSMContext):
    value = callback.data.replace("fam_", "")
    await state.update_data(family_status=value)
    await callback.message.edit_text(f"Oilaviy holat: {value}")
    await callback.message.answer("Qayerda yashaysiz? (viloyat/tuman):")
    await state.set_state(ArizaForm.address)
    await callback.answer()


@router.message(ArizaForm.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("O'z uyingizmi yoki ijarada?", reply_markup=house_type_kb())
    await state.set_state(ArizaForm.house_type)


@router.callback_query(ArizaForm.house_type, F.data.startswith("house_"))
async def get_house_type(callback: CallbackQuery, state: FSMContext):
    value = callback.data.replace("house_", "")
    await state.update_data(house_type=value)
    await callback.message.edit_text(f"Uy holati: {value}")
    await callback.message.answer("Telefon raqamingizni necha yildan beri ishlatasiz? (son, masalan: 3):")
    await state.set_state(ArizaForm.phone_years)
    await callback.answer()


@router.message(ArizaForm.phone_years)
async def get_phone_years(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat son kiriting (masalan: 3):")
        return
    await state.update_data(phone_years=int(message.text))
    await message.answer("Kafil (yaqin odam) bormi?", reply_markup=yes_no_kb())
    await state.set_state(ArizaForm.guarantor)


@router.callback_query(ArizaForm.guarantor, F.data.startswith("yn_"))
async def get_guarantor(callback: CallbackQuery, state: FSMContext):
    value = callback.data.replace("yn_", "")
    await state.update_data(guarantor=value)
    await callback.message.edit_text(f"Kafil: {value}")
    await callback.message.answer("Qaysi mahsulot olmoqchisiz?")
    await state.set_state(ArizaForm.product)
    await callback.answer()

@router.message(ArizaForm.product)
async def get_product(message: Message, state: FSMContext):
    await state.update_data(product=message.text)
    await message.answer(
        "Hozirda boshqa kredit yoki to'lovlaringiz bormi?",
        reply_markup=yes_no_kb("Bor", "Yo'q")
    )
    await state.set_state(ArizaForm.other_credit)


@router.callback_query(ArizaForm.other_credit, F.data.startswith("yn_"))
async def get_other_credit(callback: CallbackQuery, state: FSMContext, bot: Bot):
    value = callback.data.replace("yn_", "")
    await state.update_data(other_credit=value)
    await callback.message.edit_text(f"Boshqa kredit: {value}")

    if value == "Bor":
        await callback.message.answer("Oylik to'lov miqdori qancha? (so'mda yozing):")
        await state.set_state(ArizaForm.other_credit_amount)
    else:
        await state.update_data(other_credit_amount=0)
        await finish_application(callback.message, state, bot, callback.from_user)
    await callback.answer()


@router.message(ArizaForm.other_credit_amount)
async def get_other_credit_amount(message: Message, state: FSMContext, bot: Bot):
    cleaned = message.text.replace(" ", "").replace(",", "")
    if not cleaned.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting:")
        return
    await state.update_data(other_credit_amount=int(cleaned))
    await finish_application(message, state, bot, message.from_user)


async def finish_application(message: Message, state: FSMContext, bot: Bot, user):
    data = await state.get_data()
    data["user_id"] = user.id
    score = calculate_score(data)

    await save_application(data, score)
    await state.clear()

    await message.answer(
        "Rahmat! ✅\nMa'lumotlaringiz tekshirilmoqda...\nTez orada siz bilan bog'lanamiz."
    )

    text = (
        f"🆕 <b>Yangi ariza</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"🎂 Tug'ilgan yil: {data['birth_year']}\n"
        f"📞 Tel: {data['phone']}\n"
        f"💼 Ish: {data['workplace']}\n"
        f"💰 Daromad: {data['income']:,} so'm\n"
        f"👨‍👩‍👧 Oilaviy holat: {data['family_status']}\n"
        f"📍 Manzil: {data['address']}\n"
        f"🏠 Uy: {data['house_type']}\n"
        f"📱 Raqam yoshi: {data['phone_years']} yil\n"
        f"🤝 Kafil: {data['guarantor']}\n"
        f"🛒 Mahsulot: {data['product']}\n"
        f"💳 Boshqa kredit: {data['other_credit']}"
        + (f" ({data['other_credit_amount']:,} so'm/oy)" if data['other_credit'] == "Bor" else "") +
        f"\n\n⭐ <b>Ball: {score}/85</b>\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"👤 Username: @{user.username if user.username else '-'}"
    )
    await bot.send_message(ADMIN_GROUP_ID, text, reply_markup=admin_ariza_kb(user.id), parse_mode="HTML")
