from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.middlewares import DBSessionMiddleware
from config import config
from app.dao.models import BaseModel
from app.background_tasks import cleanapp, cleancodes
from aiogram.fsm.storage.memory import MemoryStorage

import uvicorn
import asyncio
# from texts_loader import TextsLoader

engine = create_engine(config.SQLALCHEMY_DATABASE_URI,
                       pool_pre_ping=True,  # проверять соединение перед использованием
                       pool_recycle=3600,  # пересоздавать соединения каждые 3600 секунд
                       pool_size=10,  # размер пула (можно настроить под нагрузку)
                       max_overflow=20
                       )
SessionMaker = sessionmaker(autoflush=False, bind=engine)
# db = SessionMaker()
BaseModel.metadata.create_all(engine)
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

dp = Dispatcher(storage=MemoryStorage())
dp.update.middleware(DBSessionMiddleware(SessionMaker))
# textsLoader = TextsLoader()
# TEXTS = textsLoader.texts

# LANGS = textsLoader.langs
# Thread(target=send, args=(bot, )).start()\
router = Router()
dp.include_routers(router)


async def run():
    asyncio.create_task(cleanapp.periodic_cleanup(SessionMaker))
    asyncio.create_task(cleancodes.periodic_cleanup_codes(SessionMaker))
    # asyncio.create_task(send(bot))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


from app.routers import index

