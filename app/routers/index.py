import time

from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app import router
from app.answers import YES_CORRECT
from app.filters import *
from app.keyboards import *
from app import texts
from app import answers
from app.dao import *

from app.form import Form
from requests import get, post
from datetime import datetime, timedelta, time, date
from sqlalchemy.orm import Session
from app.texts import *
from common import clear_state, save_schedule_and_exit, is_user_admin


@router.message(F.text.isdigit(), ~IsUserRegistered(), F.text.len() == config.CODE_LENGTH)
async def process_code_input(msg: Message, state: FSMContext, db: Session):
    wrong_attempt = await state.get_value("wrong_code_attempt")
    last_wrong_attempt = await state.get_value("wrong_last_code_attempt")
    if wrong_attempt is not None and wrong_attempt > config.MAX_WRONG_ATTEMPT_COUNT and (
            msg.date - last_wrong_attempt).total_seconds() < config.COOLDOWN_WRONG_ATTEMPT_SECONDS:
        await msg.answer(TOO_MANY_ATTEMPTS,
                         reply_markup=start_keyboard())
        return
    text = msg.text
    code = get_code(db, text)
    if code is None:
        await msg.answer(WRONG_CODE,
                         reply_markup=start_keyboard())
        wrong_attempt = await state.get_value("wrong_code_attempt")
        if wrong_attempt is None:
            wrong_attempt = 0
        await state.update_data(wrong_code_attempt=wrong_attempt + 1)
        await state.update_data(wrong_last_code_attempt=msg.date)
        return

    await state.update_data(attempt=0)

    owner = get_user(db, code.owner_id)
    group = get_group(db, owner.group_id)
    await state.update_data(group_id=owner.group_id)
    await msg.answer(ALMOST_CONNECTED.format(group.name),
                     reply_markup=start_keyboard())
    user = get_user(db, msg.from_user.id)
    if user is None:
        await msg.answer(ENTER_FIO_PROMPT)
        await state.set_state(Form.waiting_for_regular_fio)
        return
    await msg.answer(SUCCESSFULLY_CONNECTED)


@router.message(F.text == answers.GET_CODE, IsUserRegistered(), IsElder())
async def resent_code(msg: Message, state: FSMContext, db: Session):
    code = get_code_by_owner_id(db, msg.from_user.id)
    if code is not None:
        await msg.answer(PROVIDE_CODE_FOR_GROUP.format(code.code),
                         reply_markup=set_state_elder_keyboard())
        return

    new_code_text = create_code(db, msg.from_user.id)
    await msg.answer(PROVIDE_CODE_FOR_GROUP.format(new_code_text),
                     reply_markup=set_state_elder_keyboard())


@router.message(F.text.in_(["/start", answers.RESTART]))
async def cmd_start_or_restart(msg: Message, state: FSMContext, db: Session):
    await clear_state(state)
    # if not IsUserRegistered():
    #     await msg.answer(YOU_HAS_PROBLEM_WITH_REGISTER)
    #     await state.set_state(Form.waiting_for_group_name)
    #     await msg.answer(ENTER_GROUP_NAME_TEXT)
    #     return
    user = get_user(db, msg.from_user.id)
    if is_user_admin(msg.from_user.id):
        if user is None:
            keyboard = admin_start_keyboard1()
        else:
            if user.is_elder:
                keyboard = admin_start_keyboard3()
            else:
                keyboard = admin_start_keyboard2()
        await msg.answer(YOU_ARE_ADMIN, reply_markup=keyboard)
        return

    if user is None:
        await msg.answer(GREETING_TEXT, reply_markup=start_keyboard(), parse_mode=None)
        return
    if user.is_elder:
        await msg.answer(HELLO_CAN_MARK, reply_markup=set_state_elder_keyboard())
    else:
        await msg.answer(HELLO_CAN_MARK, reply_markup=set_state_regular_keyboard())


# ---------- АДМИН-ПАНЕЛЬ: НАСТРОЙКА РАСПИСАНИЯ ----------

@router.message(StateFilter(Form.schedule_editing),
                F.text == answers.BACK)
async def back_from_schedule_edit(msg: Message, state: FSMContext, db: Session):
    # Просто выходим из редактора без сохранения, если пользователь хочет в главное меню
    user = get_user(db, msg.from_user.id)
    await state.clear()
    if user is None:
        keyboard = admin_start_keyboard1()
    else:
        if user.is_elder:
            keyboard = admin_start_keyboard3()
        else:
            keyboard = admin_start_keyboard2()
    await msg.answer(MAIN_MENU, reply_markup=keyboard)
@router.message(StateFilter(Form.waiting_for_lesson_start, Form.waiting_for_lesson_end,
                            Form.waiting_for_remove_index), F.text == answers.STOP)
async def stop_process_from_schedule_edit(msg: Message, state: FSMContext, db: Session):
    # Просто выходим из редактора без сохранения, если пользователь хочет в главное меню
    user = get_user(db, msg.from_user.id)
    await state.clear()
    await state.set_state(Form.schedule_editing)
    await msg.answer(STOPPED, reply_markup=schedule_edit_keyboard())
@router.message(F.text == answers.SCHEDULE_SETTINGS)
async def admin_schedule_settings(msg: Message, state: FSMContext, db: Session):
    # Загружаем текущее расписание из БД в состояние
    current_schedule = get_schedule(db)
    await state.update_data(editable_schedule=current_schedule.copy())  # рабочая копия
    await state.set_state(Form.schedule_editing)
    await msg.answer(SCHEDULE_EDITOR_CHOOSE_ACTION, reply_markup=schedule_edit_keyboard())


@router.message(StateFilter(Form.schedule_editing), F.text == answers.ADD_LESSON)
async def add_lesson_prompt_start(msg: Message, state: FSMContext, db: Session):
    await msg.answer(ENTER_LESSON_START_PROMPT, reply_markup=stop_processing_keyboard())
    await state.set_state(Form.waiting_for_lesson_start)


@router.message(StateFilter(Form.waiting_for_lesson_start))
async def process_lesson_start_input(msg: Message, state: FSMContext, db: Session):
    start_str = msg.text.strip()
    try:
        start_time_local = datetime.strptime(start_str, "%H:%M").time()
    except ValueError:
        await msg.answer(INVALID_TIME_FORMAT)
        return

    # Предположим, что дата занятия — сегодня (или может браться из другого места)
    # В реальном проекте дату можно запросить отдельно или взять из контекста
    today = msg.date  # или другая логика
    start_local = datetime.combine(today, start_time_local)
    start_utc = start_local - timedelta(hours=3)  # переводим в UTC

    await state.update_data(new_lesson_start=start_utc)
    await state.set_state(Form.waiting_for_lesson_end)
    await msg.answer(ENTER_LESSON_END_PROMPT, reply_markup=stop_processing_keyboard())


@router.message(StateFilter(Form.waiting_for_lesson_end))
async def save_new_lesson(msg: Message, state: FSMContext, db: Session):
    end_str = msg.text.strip()

    # Парсим введённое время окончания (локальное, МСК)
    try:
        end_time_local = datetime.strptime(end_str, "%H:%M").time()
    except ValueError:
        await msg.answer(INVALID_TIME_FORMAT)
        return

    # Получаем время начала из состояния (оно уже хранится в UTC)
    data = await state.get_data()
    start_utc = data.get("new_lesson_start")
    if not start_utc:
        await msg.answer(ERROR_NO_START_TIME)
        await state.set_state(Form.schedule_editing)
        await msg.answer(SCHEDULE_EDITOR_CHOOSE_ACTION, reply_markup=schedule_edit_keyboard())
        return

    # Предполагаем, что пользователь в МСК (UTC+3)
    LOCAL_UTC_OFFSET = 3  # положительное смещение от UTC

    # 1. Преобразуем UTC-начало в локальное время (для определения даты)
    start_local = start_utc + timedelta(hours=LOCAL_UTC_OFFSET)

    # 2. Создаем локальный datetime окончания, используя дату из start_local
    end_local = datetime.combine(start_local.date(), end_time_local)

    # 3. Преобразуем локальное окончание в UTC
    end_utc = end_local - timedelta(hours=LOCAL_UTC_OFFSET)

    # 4. Сохраняем занятие в UTC (только время)
    new_lesson = {
        "start": start_utc.time().isoformat(),  # уже UTC
        "end": end_utc.time().isoformat()
    }

    editable = get_schedule(db)
    editable.append(new_lesson)

    await state.update_data(editable_schedule=editable)
    await save_schedule_and_exit(db, msg, editable)
    # Показываем пользователю время в его локальном формате (МСК)
    await msg.answer(LESSON_ADDED.format(start_local.strftime('%H:%M'), end_local.strftime('%H:%M')))

    await state.set_state(Form.schedule_editing)
    await msg.answer(SCHEDULE_EDITOR_CHOOSE_ACTION, reply_markup=schedule_edit_keyboard())


@router.message(StateFilter(Form.schedule_editing), F.text == answers.REMOVE_LESSON)
async def remove_lesson_prompt(msg: Message, state: FSMContext, db: Session):
    data = await state.get_data()
    editable = get_schedule(db)
    if not editable:
        await msg.answer(SCHEDULE_EMPTY)
        return
    # Покажем список с номерами
    lines = []
    for i, lesson in enumerate(sorted(editable, key=lambda a: time.fromisoformat(a["start"])), 1):
        start = datetime.combine(msg.date.date(), time.fromisoformat(lesson["start"]), tzinfo=pytz.UTC).astimezone(
            pytz.timezone("Europe/Moscow"))
        end = datetime.combine(msg.date.date(), time.fromisoformat(lesson["end"]), tzinfo=pytz.UTC).astimezone(
            pytz.timezone("Europe/Moscow"))
        lines.append(f'{i}. {start.strftime("%H:%M")} – {end.strftime("%H:%M")}')
    await msg.answer(SCHEDULE_CURRENT.format("\n".join(lines)))
    await msg.answer(ENTER_LESSON_NUMBER_TO_REMOVE, reply_markup=stop_processing_keyboard())
    await state.set_state(Form.waiting_for_remove_index)


@router.message(StateFilter(Form.waiting_for_remove_index))
async def process_remove_lesson(msg: Message, state: FSMContext, db: Session):
    try:
        idx = int(msg.text.strip())
    except ValueError:
        await msg.answer(ENTER_INTEGER)
        return
    data = await state.get_data()
    editable = sorted(get_schedule(db), key=lambda a: time.fromisoformat(a["start"]))
    if idx < 1 or idx > len(editable):
        await msg.answer(INDEX_OUT_OF_RANGE.format(len(editable)))
        return
    removed = editable.pop(idx - 1)
    # await state.update_data(editable_schedule=editable)
    start = datetime.combine(msg.date.date(), time.fromisoformat(removed["start"]), tzinfo=pytz.UTC).astimezone(
        pytz.timezone("Europe/Moscow"))
    end = datetime.combine(msg.date.date(), time.fromisoformat(removed["end"]), tzinfo=pytz.UTC).astimezone(
        pytz.timezone("Europe/Moscow"))
    await msg.answer(LESSON_REMOVED.format(idx, start.strftime('%H:%M'), end.strftime('%H:%M')))
    await state.set_state(Form.schedule_editing)
    await msg.answer(SCHEDULE_EDITOR_CHOOSE_ACTION, reply_markup=schedule_edit_keyboard())
    await save_schedule_and_exit(db, msg, editable)


@router.message(StateFilter(Form.schedule_editing), F.text == answers.SHOW_CURRENT)
async def show_editable_schedule(msg: Message, state: FSMContext, db: Session):
    data = await state.get_data()
    editable = get_schedule(db)
    if not editable:
        await msg.answer(SCHEDULE_EMPTY)
        return
    lines = []
    for i, lesson in enumerate(sorted(editable, key=lambda a: time.fromisoformat(a["start"])), 1):
        start = datetime.combine(msg.date.date(), time.fromisoformat(lesson["start"]), tzinfo=pytz.UTC).astimezone(
            pytz.timezone("Europe/Moscow"))
        end = datetime.combine(msg.date.date(), time.fromisoformat(lesson["end"]), tzinfo=pytz.UTC).astimezone(
            pytz.timezone("Europe/Moscow"))
        lines.append(f"{i}. {start.strftime('%H:%M')} – {end.strftime('%H:%M')}")
    await msg.answer(SCHEDULE_CURRENT_UNSAVED.format("\n".join(lines)), reply_markup=schedule_edit_keyboard())


# @router.message(StateFilter(Form.schedule_editing), F.text == answers.CANCEL_CHANGES)
# async def cancel_schedule_edit(msg: Message, state: FSMContext, db: Session):
#     await state.clear()
#     await msg.answer(CHANGES_CANCELED)
#     await msg.answer(MAIN_MENU, reply_markup=admin_start_keyboard2())


# Просмотр расписания из основного админ-меню (без редактирования)
@router.message(F.text == answers.VIEW_SCHEDULE)
async def view_schedule(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)
    if not user or not user.is_elder:
        await msg.answer(ACCESS_DENIED)
        return
    schedule = get_schedule(db)
    if not schedule:
        await msg.answer(SCHEDULE_NOT_SET)
        return
    lines = []
    for i, lesson in enumerate(schedule, 1):
        start = datetime.combine(msg.date.date(), time.fromisoformat(lesson["start"]), tzinfo=pytz.UTC).astimezone(
            pytz.timezone("Europe/Moscow"))
        end = datetime.combine(msg.date.date(), time.fromisoformat(lesson["end"]), tzinfo=pytz.UTC).astimezone(
            pytz.timezone("Europe/Moscow"))
        lines.append(f"{i}. {start.strftime('%H:%M')} – {end.strftime('%H:%M')}")
    await msg.answer(SCHEDULE_CURRENT.format("\n".join(lines)))




# Обработка "Назад" из меню управления расписанием (если не в режиме редактирования)
@router.message(F.text == answers.BACK)
async def back_to_main_menu(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)
    if user and user.is_elder:
        await msg.answer(MAIN_MENU, reply_markup=admin_start_keyboard2())
    else:
        await msg.answer(MAIN_MENU, reply_markup=start_keyboard())


@router.message(StateFilter(Form.waiting_for_regular_fio))
async def process_regular_fio(msg: Message, state: FSMContext, db: Session):
    fio = msg.text
    if len(fio) > 30:
        await msg.answer(LINE_IS_LONG)
        await msg.answer(ENTER_FIO_PROMPT)
        await state.set_state(Form.waiting_for_regular_fio)
        return

    group_id = await state.get_value("group_id")
    await state.update_data(user_fio=fio)
    await state.update_data(user_type="regular")
    await state.set_state(Form.waiting_for_confirm_registration)
    group = get_group(db, group_id)
    await msg.answer(IS_REGISTER_DATA_CORRECT.format(group.name, fio), reply_markup=is_correct_register_keyboard())

    # await state.set_state(Form.waiting_for_group_name)


# @router.message(F.text == "Подключить одногрупников")
# async def start_handler4(msg: Message, state: FSMContext, db: Session):
#     await msg.answer(GREETING_TEXT, reply_markup=start_keyboard())
#     # await state.update_data({"config_state": 0})
#     # await state.update_data({"token": None})


@router.message(F.text == answers.I_AM_REGULAR)
async def i_am_regular(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)
    if user is not None:
        await msg.answer(ALREADY_REGISTERED, reply_markup=start_keyboard())
        return
    await msg.answer(ENTER_CODE)


@router.message(F.text == answers.I_AM_ELDER)
async def i_am_elder(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)
    if user is not None:
        group = get_group(db, user.group_id)
        if group is not None:
            await msg.answer(ALREADY_REGISTERED_AND_HAVE_GROUP, reply_markup=start_keyboard())
            return
        await msg.answer(ALREADY_REGISTERED, reply_markup=start_keyboard())
        return
    await state.set_state(Form.waiting_for_elder_fio)
    await msg.answer(ENTER_FIO)


@router.message(StateFilter(Form.waiting_for_elder_fio))
async def process_elder_fio(msg: Message, state: FSMContext, db: Session):
    fio = msg.text
    if len(fio) > 30:
        await msg.answer(LINE_IS_LONG)
        await msg.answer(ENTER_FIO)
        await state.set_state(Form.waiting_for_elder_fio)
        return
    await state.update_data(user_fio=fio)
    await msg.answer(REGISTERED_NOW_ENTER_GROUP)
    await state.set_state(Form.waiting_for_group_name)


@router.message(StateFilter(Form.waiting_for_group_name))
async def process_group_name(msg: Message, state: FSMContext, db: Session):
    group_name = msg.text
    if len(group_name) > 10:
        await msg.answer(LINE_IS_LONG)
        await msg.answer(NOW_ENTER_GROUP)
        await state.set_state(Form.waiting_for_group_name)
        return
    user_fio = await state.get_value("user_fio")
    group = get_group_by_name(db, group_name)
    if group is not None:
        await msg.answer(GROUP_ALREADY_EXIST_WITH_THIS_NAME, parse_mode=None)
        await state.set_state(Form.waiting_for_group_name)
        await msg.answer(NOW_ENTER_GROUP)
        return
    await state.update_data(group_name=group_name)
    await state.update_data(user_type="elder")
    await state.set_state(Form.waiting_for_confirm_registration)
    await msg.answer(IS_REGISTER_DATA_CORRECT.format(group_name, user_fio), reply_markup=is_correct_register_keyboard())


@router.message(StateFilter(Form.waiting_for_confirm_registration))
async def process_group_name(msg: Message, state: FSMContext, db: Session):
    user_fio = await state.get_value("user_fio")
    group_name = await state.get_value("group_name")
    user_type = await state.get_value("user_type")
    if msg.text == YES_CORRECT:
        if user_type == "elder":
            user = create_user(db, msg.from_user.id, user_fio, None, True)
            new_group = create_group(db, msg.from_user.id, group_name)
            user.group_id = new_group.group_id
            await msg.answer(GROUP_CREATED_YOU_ARE_ELDER)
            new_code_text = create_code(db, msg.from_user.id)
            await msg.answer(PROVIDE_CODE_FOR_GROUP.format(new_code_text), reply_markup=set_state_elder_keyboard())
        else:
            group_id = await state.get_value("group_id")
            create_user(db, msg.from_user.id, user_fio, group_id, False)
            await msg.answer(REGISTERED_SUCCESS, reply_markup=set_state_regular_keyboard())
        db.commit()
        await state.clear()
    elif user_type == "elder":
        await state.set_state(Form.waiting_for_elder_fio)
        await msg.answer(ENTER_FIO)
    else:
        await state.clear()
        await msg.answer(ENTER_CODE)


@router.message(F.text == answers.I_AM_HERE_NOW, IsUserRegistered())
async def mark_current_lesson(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)
    if user.is_elder:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard3()
        else:
            keyboard = set_state_elder_keyboard()
    else:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard2()
        else:
            keyboard = set_state_regular_keyboard()

    tm = get_schedule_item_by_datetime(get_schedule(db), msg.date)

    if tm is None:
        await msg.answer(LESSON_NOT_STARTED, reply_markup=keyboard)
        return
    marker = get_marker_by_datetime(db, msg.from_user.id, msg.date)
    if marker is not None:
        await msg.answer(
            ALREADY_MARKED_FOR_CURRENT_LESSON.format(tm[0] + 1,
                                                     tm[1].astimezone(pytz.timezone("Europe/Moscow")).strftime(
                                                         "%H:%M"),
                                                     tm[2].astimezone(pytz.timezone("Europe/Moscow")).strftime(
                                                         "%H:%M")), reply_markup=keyboard)
        return
    d = msg.date

    create_marker(db, msg.from_user.id, msg.date)
    await msg.answer(
        MARKED_FOR_LESSON.format(tm[0] + 1, tm[1].astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%H:%M"),
                                 tm[2].astimezone(pytz.timezone("Europe/Moscow")).strftime(
                                     "%H:%M")), reply_markup=keyboard)


@router.message(F.text == answers.I_AM_HERE_TODAY, IsUserRegistered())
async def mark_today(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)
    if user.is_elder:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard3()
        else:
            keyboard = set_state_elder_keyboard()
    else:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard2()
        else:
            keyboard = set_state_regular_keyboard()
    markers = get_markers(db, msg.from_user.id)
    schedule = get_schedule(db)
    if len(markers) >= len(schedule):
        await msg.answer(ALREADY_MARKED_FOR_TODAY, reply_markup=keyboard)
        return
    for s in schedule:
        start = time.fromisoformat(s["start"])
        end = time.fromisoformat(s["end"])
        f = False
        for m in markers:
            if start <= m.timestamp.astimezone(pytz.UTC).time() <= end:
                f = True
                break
        if not f:
            dt = datetime.combine(msg.date.date(), start, tzinfo=pytz.UTC)

            create_marker(db, msg.from_user.id, dt, msg.date, True)

    await msg.answer(MARKED_FOR_TODAY, reply_markup=keyboard)


@router.message(F.text == answers.GET_CHECKS_NOW, IsUserRegistered())
async def get_marks_current_lesson(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)

    if user.is_elder:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard3()
        else:
            keyboard = set_state_elder_keyboard()
    else:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard2()
        else:
            keyboard = set_state_regular_keyboard()
    markers = get_markers_by_datetime_and_group(db, user.group_id, msg.date)
    tm = get_schedule_item_by_datetime(get_schedule(db), msg.date)
    if tm is None:
        await msg.answer(LESSON_NOT_STARTED, reply_markup=keyboard)
        return
    if not markers:
        await msg.answer(NO_MARKS_YET, reply_markup=keyboard)
        return

    await msg.answer(MARKED_NOW_HEADER.format(tm[0] + 1, tm[1].astimezone(pytz.timezone("Europe/Moscow")).strftime('%H:%M'),
                                    tm[2].astimezone(pytz.timezone("Europe/Moscow")).strftime('%H:%M')), reply_markup=keyboard)

    line = []
    for m in markers:
        user = get_user(db, m.user_id)
        line.append(MARKED_USER_LINE.format(user.user_fio, m.add_timestamp.astimezone(pytz.timezone("Europe/Moscow")).strftime('%H:%M')))

    line.append(SEPARATOR)
    line = "\n".join(line)
    await msg.answer(line, reply_markup=keyboard)


@router.message(F.text == answers.GET_CHECKS_TODAY, IsUserRegistered())
async def get_marks_today(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)

    if user.is_elder:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard3()
        else:
            keyboard = set_state_elder_keyboard()
    else:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard2()
        else:
            keyboard = set_state_regular_keyboard()
    markers = get_markers_by_date_and_group(db, user.group_id, msg.date.date())

    if not markers:
        await msg.answer(NO_MARKS_YET, reply_markup=keyboard)
        return
    schedule = sorted(get_schedule(db), key=lambda a: time.fromisoformat(a["start"]))

    await msg.answer(MARKED_TODAY_HEADER, reply_markup=keyboard)
    for s in schedule:
        line = []
        start = time.fromisoformat(s["start"])
        end = time.fromisoformat(s["end"])
        dts = datetime.combine(msg.date.date(), start, tzinfo=pytz.UTC)
        dte = datetime.combine(msg.date.date(), end, tzinfo=pytz.UTC)

        markers_in_lesson = list(filter(lambda m: start <= m.timestamp.astimezone(pytz.UTC).time() <= end, markers))
        if not markers_in_lesson:
            continue

        line.append(MARKED_LESSON_LINE.format(schedule.index(s) + 1,
                                          dts.astimezone(pytz.timezone("Europe/Moscow")).strftime('%H:%M'),
                                          dte.astimezone(pytz.timezone("Europe/Moscow")).strftime('%H:%M')))
        # if not markers_in_lesson:
        #     line += "Никто не отметился"
        for m in markers_in_lesson:
            user = get_user(db, m.user_id)
            line.append(MARKED_USER_LINE.format(user.user_fio,
                                            m.add_timestamp.astimezone(pytz.timezone("Europe/Moscow")).strftime(
                                                '%H:%M')))
        line.append(SEPARATOR)
        await msg.answer("\n".join(line), reply_markup=keyboard)


@router.message(F.text == answers.GET_CHECKS_ON_DATE, IsUserRegistered())
async def prompt_for_date(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)

    await msg.answer(ENTER_DATE_PROMPT)

    await state.set_state(Form.waiting_for_date_for_checks)


@router.message(StateFilter(Form.waiting_for_date_for_checks))
async def process_date_for_marks(msg: Message, state: FSMContext, db: Session):
    user = get_user(db, msg.from_user.id)
    if user.is_elder:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard3()
        else:
            keyboard = set_state_elder_keyboard()
    else:
        if is_user_admin(msg.from_user.id):
            keyboard = admin_start_keyboard2()
        else:
            keyboard = set_state_regular_keyboard()
    text = msg.text
    # date = None
    try:
        d = text.split(".")
        d.reverse()
        d = "-".join(d)

        date_parsed = date.fromisoformat(d)
    except ValueError:
        await msg.answer(INVALID_DATE_FORMAT, reply_markup=keyboard)
        return
    rz = msg.date.date() - date_parsed

    if rz.days >= 30:
        await msg.answer(OLD_DATE_WARNING, reply_markup=keyboard)

    markers = get_markers_by_date_and_group(db, user.group_id, date_parsed)

    if not markers:
        await msg.answer(NO_MARKS_YET, reply_markup=keyboard)
        return
    schedule = sorted(get_schedule(db), key=lambda a: time.fromisoformat(a["start"]))


    await msg.answer(MARKED_ON_DATE_HEADER.format(text), reply_markup=keyboard)
    for s in schedule:
        line = []
        start = time.fromisoformat(s["start"])
        end = time.fromisoformat(s["end"])
        dts = datetime.combine(msg.date.date(), start, tzinfo=pytz.UTC)
        dte = datetime.combine(msg.date.date(), end, tzinfo=pytz.UTC)
        markers_in_lesson = list(filter(lambda m: start <= m.timestamp.astimezone(pytz.UTC).time() <= end, markers))
        if not markers_in_lesson:
            continue
        line.append(MARKED_LESSON_LINE.format(schedule.index(s) + 1,
                                          dts.astimezone(pytz.timezone("Europe/Moscow")).strftime('%H:%M'),
                                          dte.astimezone(pytz.timezone("Europe/Moscow")).strftime('%H:%M')))
        # if not markers_in_lesson:
        #     line += "Никто не отметился"
        for m in markers_in_lesson:
            user = get_user(db, m.user_id)
            line.append(MARKED_USER_LINE.format(user.user_fio,
                                            m.add_timestamp.astimezone(pytz.timezone("Europe/Moscow")).strftime(
                                                '%H:%M')))

        line.append(SEPARATOR)
        await msg.answer("\n".join(line), reply_markup=keyboard)

    # await state.set_state(Form.waiting_for_group_name)

# @router.message(~IsUserRegistered())
# async def shoot_unregister_full(msg: Message, state: FSMContext, db: Session):
#     await msg.answer(YOU_HAS_PROBLEM_WITH_REGISTER, reply_markup=start_keyboard())
