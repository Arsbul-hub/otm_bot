import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app import run
import uvicorn



# def run_bot():

#



# app = FastAPI()


if __name__ == "__main__":
    # import uvicornr
    #
    #
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
    #run()
    #uvicorn.run(app, host="127.0.0.1", port=5000, ssl_keyfile="./web/key.pem", ssl_certfile="./web/cert.pem")
    # run_bot()
