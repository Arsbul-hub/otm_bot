from aiogram.filters import Filter
from aiogram.types import Message
from app.dao import get_user
from app import db

class IsUserRegistered(Filter):
    """
    Фильтр проверяет, что пользователь полностью зарегистрирован
    (существует в БД и привязан к группе).
    """
    async def __call__(self, message: Message) -> bool:
        user = get_user(db, message.from_user.id)
        return user is not None

class IsElder(Filter):
    async def __call__(self, message: Message) -> bool:
        user = get_user(db, message.from_user.id)
        return user.is_elder