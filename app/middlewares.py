import logging

from sqlalchemy.orm import Session
from aiogram import BaseMiddleware

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def __call__(self, handler, event, data):
        try:
            with self.session_maker() as session:
                data["db"] = session
                return await handler(event, data)
        except Exception as e:
            logging.error(f"DB error: {e}")

            if hasattr(event, "answer"):
                await event.answer("Произошла ошибка, попробуйте позже.")
            raise