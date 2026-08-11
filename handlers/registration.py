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
