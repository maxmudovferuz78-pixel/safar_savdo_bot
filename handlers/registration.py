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