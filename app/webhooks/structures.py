from pydantic import BaseModel


class MessagesBody(BaseModel):
    messages: list # [{"user_id": "", "text": ""}]