from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import FILIALS


def yes_no_kb(yes_text="Ha", no_text="Yo'q"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=yes_text, callback_data=f"yn_{yes_text}"),
         InlineKeyboardButton(text=no_text, callback_data=f"yn_{no_text}")]
    ])


def family_status_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Oilali", callback_data="fam_Oilali"),
         InlineKeyboardButton(text="Turmush qurmagan", callback_data="fam_Turmush qurmagan")]
    ])


def house_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="O'z uy", callback_data="house_O'z uy"),
         InlineKeyboardButton(text="Ijara", callback_data="house_Ijara")]
    ])