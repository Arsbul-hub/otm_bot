import datetime
import logging
import asyncio

import pytz
from sqlalchemy.orm import Session

from app.dao.models import Marker
from config import config


async def periodic_cleanup(SessionMaker):
    """
    Фоновая задача: раз в сутки удаляет маркеры старше MARKER_EXPIRES_DAYS.
    """
    while True:
        try:
            with SessionMaker() as session:

                expiry_date = datetime.datetime.now(pytz.UTC).date() - datetime.timedelta(days=config.MARKER_EXPIRES_DAYS)
                expiry_datetime = datetime.datetime.combine(expiry_date, datetime.time.min, tzinfo=pytz.UTC)
                deleted_count = session.query(Marker).filter(
                    Marker.timestamp < expiry_datetime
                ).delete(synchronize_session=False)
                session.commit()

                if deleted_count:
                    logging.info(f"[Cleanup] Удалено {deleted_count} старых маркеров")
        except Exception as e:
            logging.error(f"[Cleanup] Ошибка: {e}")

        await asyncio.sleep(24 * 60 * 60)