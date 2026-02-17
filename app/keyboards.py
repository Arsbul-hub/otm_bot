from aiogram.types import InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.answers import *
from .config import URL


def start_keyboard():
    keyboard = [
        [KeyboardButton(text=START_MESSAGE)]
    ]
    kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

    return kb


# def change_date_keyboard():
#

def open_app_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(text=OPEN_APP_MESSAGE, web_app=WebAppInfo(url=URL))
    return kb.as_markup()
