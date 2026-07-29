import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ_BU_YERGA")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "-1000000000000"))

# PostgreSQL ulanish manzili. Format:
# postgresql://foydalanuvchi:parol@host:port/baza_nomi
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/safar_savdo")

# 6 ta filial va ularning to'lov qabul qiluvchi plastik kartalari.
# Har bir filialning karta raqamini shu yerda o'zgartiring.
FILIALS = {
    "filial_1": {"name": "1-filial (Chilonzor)", "card": "8600 0000 0000 0001"},
    "filial_2": {"name": "2-filial (Yunusobod)", "card": "8600 0000 0000 0002"},
    "filial_3": {"name": "3-filial (Sergeli)", "card": "8600 0000 0000 0003"},
    "filial_4": {"name": "4-filial (Mirzo Ulug'bek)", "card": "8600 0000 0000 0004"},
    "filial_5": {"name": "5-filial (Bektemir)", "card": "8600 0000 0000 0005"},
    "filial_6": {"name": "6-filial (Uchtepa)", "card": "8600 0000 0000 0006"},
}
