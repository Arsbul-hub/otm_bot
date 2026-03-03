from datetime import datetime, time

from aiogram.utils import keyboard


import pytz

from app.keyboards import schedule_edit_keyboard
from app.texts import SCHEDULE_SAVED

from app.dao import set_schedule
from config import config


def get_schedule_item_by_datetime(times, dt_utc):
    times = sorted(times, key=lambda t: time.fromisoformat(t["start"]))
    for tm in times:
        start = time.fromisoformat(tm["start"])
        end = time.fromisoformat(tm["end"])
        if start <= dt_utc.time() <= end:
            return times.index(tm), datetime.combine(dt_utc.date(), time.fromisoformat(tm["start"]), tzinfo=pytz.UTC), datetime.combine(
                dt_utc.date(), time.fromisoformat(tm["end"]), tzinfo=pytz.UTC)
def get_marker_by_lesson(markers, tm_start, tm_end):
    for m in markers:
        start = time.fromisoformat(tm_start)
        end = time.fromisoformat(tm_end)
        if start <= m.time() <= end:
            return m


async def clear_state(state):
    wrong_attempt = await state.get_value("wrong_code_attempt")
    await state.clear()
    await state.update_data(wrong_code_attempt=wrong_attempt)



async def save_schedule_and_exit(db, msg, schedule_list):


    set_schedule(db, schedule_list)
    await msg.answer(SCHEDULE_SAVED, reply_markup=schedule_edit_keyboard())
    # await state.clear()
    # # Вернёмся в админское меню
    # await msg.answer(MAIN_MENU, reply_markup=admin_start_keyboard2())


def is_user_admin(user_id):
    return user_id == config.DEFAULT_ADMIN_USER_ID