from typing import Any, List

from app.domain.chatbot.repository import (
    create_chatbot,
    delete_chatbot_by_id,
    get_all_chatbots,
    get_chatbot_by_id,
    patch_chatbot_by_id,
)
from app.domain.chatbot.schemas import ChatBotCreateUpdate, ChatBotResponseDTO
from app.domain.services.verification import check_existing, check_superuser
from app.exceptions.chatbot_exceptions import ChatBotNotFoundException


async def get_all_chatbots_service(current_user: Any) -> List[ChatBotResponseDTO]:
    check_superuser(current_user)
    return await get_all_chatbots()


async def create_chatbot_by_id_service(
    current_user: Any, chatbot: ChatBotCreateUpdate
) -> ChatBotResponseDTO:
    check_superuser(current_user)
    return await create_chatbot(chatbot)


async def patch_chatbot_by_id_service(
    id: int, current_user: Any, update_chatbot: ChatBotCreateUpdate
) -> ChatBotResponseDTO:
    check_superuser(current_user)
    chatbot = await get_chatbot_by_id(id)
    check_existing(chatbot, ChatBotNotFoundException)

    chatbot = await patch_chatbot_by_id(chatbot, update_chatbot)

    return chatbot


async def delete_chatbot_by_id_service(
    id: int,
    current_user: Any,
):
    check_superuser(current_user)
    chatbot = await get_chatbot_by_id(id)
    check_existing(chatbot, ChatBotNotFoundException)
    await delete_chatbot_by_id(chatbot)
