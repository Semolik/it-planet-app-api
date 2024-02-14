
from schemas.chats import ChatWithUsers


def set_chat_info(chat, unread_count) -> ChatWithUsers:
    chat_obj = ChatWithUsers.model_validate(chat, from_attributes=True)
    chat_obj.unreaded = unread_count
    return chat_obj
