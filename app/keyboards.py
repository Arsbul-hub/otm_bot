from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app import answers

def start_keyboard():
    keyboard = [
        [KeyboardButton(text=answers.I_AM_REGULAR), KeyboardButton(text=answers.I_AM_ELDER)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def admin_start_keyboard1():
    keyboard = [
        [KeyboardButton(text=answers.I_AM_REGULAR), KeyboardButton(text=answers.I_AM_ELDER)],
        [KeyboardButton(text=answers.SCHEDULE_SETTINGS)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def admin_start_keyboard2():
    keyboard = [
        [KeyboardButton(text=answers.I_AM_HERE_NOW), KeyboardButton(text=answers.I_AM_HERE_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_NOW), KeyboardButton(text=answers.GET_CHECKS_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_ON_DATE)],
        [KeyboardButton(text=answers.SCHEDULE_SETTINGS)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
def admin_start_keyboard3():
    keyboard = [
        [KeyboardButton(text=answers.I_AM_HERE_NOW), KeyboardButton(text=answers.I_AM_HERE_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_NOW), KeyboardButton(text=answers.GET_CHECKS_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_ON_DATE)],
        [KeyboardButton(text=answers.SCHEDULE_SETTINGS), KeyboardButton(text=answers.GET_CODE)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def schedule_management_keyboard():
    keyboard = [
        [KeyboardButton(text=answers.VIEW_SCHEDULE)],
        [KeyboardButton(text=answers.EDIT_SCHEDULE)],
        [KeyboardButton(text=answers.BACK)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def schedule_edit_keyboard():
    keyboard = [
        [KeyboardButton(text=answers.ADD_LESSON)],
        [KeyboardButton(text=answers.REMOVE_LESSON)],
        [KeyboardButton(text=answers.SHOW_CURRENT)],
        # [KeyboardButton(text=answers.SAVE_AND_EXIT)],
        # [KeyboardButton(text=answers.CANCEL_CHANGES)],
        [KeyboardButton(text=answers.BACK)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def admin_back_keyboard():
    keyboard = [[KeyboardButton(text=answers.BACK)]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
def set_state_regular_keyboard():
    keyboard = [
        [KeyboardButton(text=answers.I_AM_HERE_NOW), KeyboardButton(text=answers.I_AM_HERE_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_NOW), KeyboardButton(text=answers.GET_CHECKS_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_ON_DATE)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def set_state_elder_keyboard():
    keyboard = [
        [KeyboardButton(text=answers.I_AM_HERE_NOW), KeyboardButton(text=answers.I_AM_HERE_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_NOW), KeyboardButton(text=answers.GET_CHECKS_TODAY)],
        [KeyboardButton(text=answers.GET_CHECKS_ON_DATE)],
        [KeyboardButton(text=answers.GET_CODE)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def is_correct_register_keyboard():
    keyboard = [
        [KeyboardButton(text=answers.YES_CORRECT), KeyboardButton(text=answers.NO_INCORRECT)],

    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
def stop_processing_keyboard():
    keyboard = [
        [KeyboardButton(text=answers.STOP)],

    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
