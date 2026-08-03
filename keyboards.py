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

def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )


def filial_kb():
    rows = []
    for key, info in FILIALS.items():
        rows.append([InlineKeyboardButton(text=info["name"], callback_data=f"filial_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_ariza_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ariza_ok_{user_id}"),
         InlineKeyboardButton(text="❌ Rad etish", callback_data=f"ariza_no_{user_id}")]
    ])


def admin_payment_kb(payment_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_ok_{payment_id}"),
         InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay_no_{payment_id}")]
    ])
