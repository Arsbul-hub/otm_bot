from app import webhookapp, bot
from app.webhooks.structures import MessagesBody
import aiogram


@webhookapp.post("/webhook/send_message")
async def send_message(body: MessagesBody):
    
    for message in body.messages:
        user_id = message["user_id"]
        message_text = message["text"]
        try:
            await bot.send_message(user_id, message_text)
        except aiogram.exceptions.TelegramBadRequest:
            return {"status": 400, "message": "Telegram server says - Bad Request: chat not found"}
    return {"status": 200}