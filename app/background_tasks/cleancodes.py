import datetime
import logging
import asyncio

from app.dao.models import Code

async def periodic_cleanup_codes(SessionMaker):
    """
    Фоновая задача: раз в час удаляет просроченные коды (expires < текущее UTC).
    """
    while True:
        try:
            with SessionMaker() as session:

                now_utc = datetime.datetime.now(datetime.timezone.utc)

                deleted_count = session.query(Code).filter(
                    Code.expires < now_utc
                ).delete(synchronize_session=False)
                session.commit()

                if deleted_count:
                    logging.info(f"[Cleanup Codes] Удалено {deleted_count} просроченных кодов")
        except Exception as e:
            logging.error(f"[Cleanup Codes] Ошибка: {e}")


        await asyncio.sleep(60 * 60)  # 3600 секунд