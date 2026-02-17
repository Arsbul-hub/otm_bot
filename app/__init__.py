from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
from .config import API_TOKEN
import uvicorn
import asyncio
# from texts_loader import TextsLoader
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())
# textsLoader = TextsLoader()
# TEXTS = textsLoader.texts

# LANGS = textsLoader.langs
# Thread(target=send, args=(bot, )).start()\
router = Router()
dp.include_routers(router)
webhookapp = FastAPI()
async def start_webhooks():
    uvicorn_config = uvicorn.Config(webhookapp, host="127.0.0.2", port=5000)
    uvicron_server = uvicorn.Server(uvicorn_config)
    await uvicron_server.serve()
    
    
async def run():
    # asyncio.create_task(send(bot))
    asyncio.create_task(start_webhooks())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


from app.routers import index
from app.webhooks.webhooks import *
