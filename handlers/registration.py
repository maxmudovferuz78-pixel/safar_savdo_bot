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