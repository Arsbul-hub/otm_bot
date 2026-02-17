import time
from datetime import datetime
from threading import Thread

from aiogram import F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app import router
from app.keyboards import *
from app.texts import *
from app.answers import *
from app.config import *
from app.widgets.aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from requests import get, post


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer(GREETING_TEXT, reply_markup=start_keyboard())
    await state.update_data({"average_period_length": None})
    await state.update_data({"cycle_period_length": None})
    await state.update_data({"last_average_date": None})
    await state.update_data({"config_state": 0})
    await state.update_data({"token": None})


# @router.message(F.text == START_MESSAGE)
# async def start_handler(msg: Message, state: FSMContext):
#     await msg.answer(LAST_AVERAGE_DATE_TEXT, reply_markup=await SimpleCalendar(locale='ru_ru').start_calendar())


# @router.callback_query(SimpleCalendarCallback.filter())
# async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
#     calendar = SimpleCalendar(
#         locale=await get_user_locale(callback_query.from_user), show_alerts=True
#     )
#     calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
#     selected, date = await calendar.process_selection(callback_query, callback_data)
#     if selected:
#         format_date = date.strftime("%Y-%m-%d")
#         await callback_query.message.answer(
#             f'Ты выбрала {format_date}'
#         )
#         await state.update_data({"last_average_date": format_date})
#         await state.update_data({"config_state": 1})
#         await callback_query.message.answer(CHANGE_CYCLE_PERIOD_LENGTH_TEXT)


# @router.message()
# async def start_handler(msg: Message, state: FSMContext):
#     config_state = (await state.get_data()).get("config_state")
#     print(config_state)
#     if config_state == 1:
#         await msg.answer(CHANGE_AVERAGE_PERIOD_LENGTH_TEXT)
#         await state.update_data({"cycle_period_length": int(msg.text)})
#         await state.update_data({"config_state": 2})
#     if config_state == 2:
#         await msg.answer(SAVE_CONFIG_TEXT, reply_markup=open_app_keyboard())
#         # await state.update_data({"average_period_length": int(msg.text)})
#         average_period_length = int(msg.text)
#         cycle_period_length = (await state.get_data()).get("cycle_period_length")
#         last_average_date = (await state.get_data()).get("last_average_date")
#         await state.update_data({"config_state": 3})
#         token = None
#         while token is None:
#             request = get(f"{URL}/get_access_token", params={"user_id": msg.from_user.id}, verify=CERTIFICATE_VERIFY)
#             if request.status_code == 200:
#                 data = request.json()
#                 token = data["token"]
#         await state.update_data({"token": token})
#         params = {
#             "average_period_length": average_period_length,
#             "cycle_period_length": cycle_period_length,
#             "last_average_date": last_average_date,
#             "token": token,
#             "user_id": msg.from_user.id,
#         }
#         while True:
#             request = post(f"{URL}/add_user_data", params=params, verify=CERTIFICATE_VERIFY)
#             if request.status_code == 200:
#                 break
        # request = get(f"{URL}/get_menstruation_days", params=params)
        # await msg.answer(str(request.json()))
        # await msg.answer(str(request.json()))

# @router.message(F.text == CHANGE_AVERAGE_PERIOD_LENGTH_TEXT)
# async def start_handler(msg: Message, state: FSMContext):

# @router.message(F.text == SAVE_CONFIG_TEXT)
# async def start_handler(msg: Message, state: FSMContext):
#     await msg.answer(, reply_markup=)
