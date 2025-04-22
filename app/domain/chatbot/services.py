from typing import Any, List

from fastapi import status

from app.domain.chatbot.model import ChatBot
from app.domain.chatbot.repository import (
    create_chatbot,
    delete_chatbot,
    get_all_chatbots,
    get_chatbot_by_id,
    patch_chatbot_by_id,
)
from app.domain.chatbot.schemas import ChatBotCreateUpdate, ChatBotResponseDTO
from app.domain.services.verification import (
    CustomException,
    check_existing,
    check_superuser,
)


async def get_all_chatbots_service(current_user: Any) -> List[ChatBotResponseDTO]:
    check_superuser(current_user)
    return await get_all_chatbots()


async def create_chatbot_by_id_service(
    current_user: Any, chatbot: ChatBotCreateUpdate
) -> ChatBotResponseDTO:
    check_superuser(current_user)
    return await create_chatbot(chatbot)


async def patch_chatbot_by_id_service(
    id: int, update_chatbot: ChatBotCreateUpdate
) -> ChatBotResponseDTO:
    chatbot = get_chatbot_by_id(id)
    check_existing(chatbot, "해당 챗봇 프롬프트가 없습니다.", "chatbot_not_found")

    chatbot = await patch_chatbot_by_id(chatbot, update_chatbot)

    return chatbot


async def delete_chatbot_by_id_service(
    id: int,
    current_user: Any,
):
    check_superuser(current_user)
    chatbot = get_chatbot_by_id(id)
    check_existing(chatbot, "해당 챗봇 프롬프트가 없습니다.", "chatbot_not_found")
    await delete_chatbot(chatbot)
