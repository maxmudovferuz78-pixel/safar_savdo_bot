from aiogram.fsm.state import State, StatesGroup


class ArizaForm(StatesGroup):
    full_name = State()
    birth_year = State()
    phone = State()
    workplace = State()
    income = State()
    family_status = State()
    address = State()
    house_type = State()
    phone_years = State()
    guarantor = State()
    product = State()
    other_credit = State()
    other_credit_amount = State()


class TolovForm(StatesGroup):
    choosing_filial = State()
    entering_amount = State()
