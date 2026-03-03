import datetime
import json
from random import randint

import pytz
from sqlalchemy import and_, func
from app import config
from app.dao.models import *



def create_code(db, user_id) -> int:
    new_code = Code()
    new_code.owner_id = user_id
    new_code.code = randint(10**(config.CODE_LENGTH - 1), 10**config.CODE_LENGTH - 1)
    new_code.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=config.CODE_EXPIRES_HOURS)
    db.add(new_code)
    db.commit()
    return new_code.code

def get_code(db, code_text) -> Code:
    return db.query(Code).get(int(code_text))
def get_code_by_owner_id(db, owner_id) -> Code:
    return db.query(Code).filter_by(owner_id=str(owner_id)).first()
def delete_code(db, code_id):
    code = db.query(Code).get(code_id)
    if code:
        db.delete(code)
        db.commit()

def create_group(db, user_id, group_name) -> Group:
    new_group = Group()
    new_group.owner_id = user_id
    new_group.name = str(group_name).strip().lower()
    db.add(new_group)
    db.commit()
    return new_group

def create_user(db, user_id, user_fio, group_id, is_elder):
    new_user = User()
    new_user.user_id = str(user_id)
    new_user.is_elder = is_elder
    new_user.group_id = group_id
    new_user.user_fio = user_fio

    db.add(new_user)
    db.commit()
    return new_user
def get_group_by_name(db, group_name) -> Group:
    return db.query(Group).filter_by(name=str(group_name).strip().lower()).first()
def get_group(db, group_id) -> Group:
    return db.query(Group).get(group_id)
def get_user(db, user_id) -> User:
    return db.query(User).get(str(user_id))



def set_config(db, key, value):
    conf = db.query(EditableConfig).filter(EditableConfig.key == key).first()
    if conf is None:
        conf = EditableConfig(key=key, value=value)
        db.add(conf)
    else:
        conf.value = value
    db.commit()


def get_config(db, key):
    return db.query(EditableConfig).filter(EditableConfig.key == key).first()


def get_schedule(db):
    """Возвращает список занятий [{'start': '...', 'end': '...'}, ...] или пустой список"""
    conf = get_config(db, "schedule")
    if conf and conf.value:
        try:
            return json.loads(conf.value)
        except:
            return []
    return []


def set_schedule(db, schedule_list):
    """Сохраняет список занятий в JSON"""
    set_config(db, "schedule", json.dumps(schedule_list, ensure_ascii=False))


def get_markers(db, user_id):
    return db.query(Marker).filter_by(user_id=str(user_id)).all()
def get_marker_by_datetime(db, uid, dt_utc: datetime.datetime) -> Marker:
    # 1. Получаем расписание
    times = get_schedule(db)
    if not times:
        return None

    # 2. Определяем интервал в локальном времени, в который попадает dt_local.time()
    interval = get_schedule_item_by_datetime(times, dt_utc)  # возвращает (start_time, end_time)
    if interval is None:
        return None

    _, start_utc, end_utc = interval

    # 3. Строим локальные datetime для границ интервала (используем дату из dt_local)


    # 4. Переводим локальные границы в UTC (фиксированное смещение для МСК = +3)
    # LOCAL_UTC_OFFSET = 3  # положительное смещение от UTC
    # start_utc = start_local - datetime.timedelta(hours=LOCAL_UTC_OFFSET)
    # end_utc = end_local - datetime.timedelta(hours=LOCAL_UTC_OFFSET)

    # 5. Ищем маркер в этом UTC-диапазоне
    return db.query(Marker).filter_by(user_id=str(uid)).filter(
        Marker.timestamp.between(start_utc, end_utc)
    ).first()
def get_markers_by_datetime_and_group(db, grop_id, dt_utc: datetime.datetime) -> list:
    # 1. Получаем расписание

    times = get_schedule(db)
    if not times:
        return None

    # 2. Определяем интервал в локальном времени, в который попадает dt_local.time()
    interval = get_schedule_item_by_datetime(times, dt_utc)  # возвращает (start_time, end_time)
    if interval is None:
        return None

    n, start_utc, end_utc = interval
    users = db.query(User).filter_by(group_id=str(grop_id)).all()
    # 3. Строим локальные datetime для границ интервала (используем дату из dt_local)


    # 4. Переводим локальные границы в UTC (фиксированное смещение для МСК = +3)
    # LOCAL_UTC_OFFSET = 3  # положительное смещение от UTC
    # start_utc = start_local - datetime.timedelta(hours=LOCAL_UTC_OFFSET)
    # end_utc = end_local - datetime.timedelta(hours=LOCAL_UTC_OFFSET)

    # 5. Ищем маркер в этом UTC-диапазоне
    return db.query(Marker).filter(
        and_(Marker.timestamp.between(start_utc, end_utc), Marker.user_id.in_(list(map(lambda a: a.user_id, users))))
    ).all()


def get_markers_by_date_and_group(db, grop_id, d: datetime.date) -> list:
    users = db.query(User).filter_by(group_id=str(grop_id)).all()
    return db.query(Marker).filter(and_(func.date(Marker.timestamp) == d), Marker.user_id.in_(list(map(lambda a: a.user_id, users)))).all()
def create_marker(db, user_id, timestamp, add_timestamp=None, is_auto=False):
    new_marker = Marker()
    new_marker.user_id = user_id
    new_marker.timestamp = timestamp.astimezone(pytz.UTC)
    new_marker.all_day = is_auto
    if add_timestamp is None:
        add_timestamp = timestamp
    new_marker.add_timestamp = add_timestamp.astimezone(pytz.UTC)

    db.add(new_marker)
    db.commit()

from common import get_schedule_item_by_datetime