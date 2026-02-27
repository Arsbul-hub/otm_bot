from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_elder_fio = State()
    waiting_for_regular_fio = State()
    waiting_for_group_name = State()
    waiting_for_confirm_registration = State()
    schedule_editing = State()          # активный режим редактирования (храним текущий список в data)
    waiting_for_lesson_start = State()  # ожидание start нового занятия
    waiting_for_lesson_end = State()    # ожидание end
    waiting_for_remove_index = State()  # ожидание номера удаляемого занятия
    waiting_for_date_for_checks = State()  # ожидание номера удаляемого занятия