from fastapi import status

from app.domain.chatbot.chatbot_model import ChatBot
from app.domain.chatbot.chatbot_schemas import ChatBotCreateUpdate
from app.domain.user.user_models import BaseUser
from app.utils.exception import CustomException, check_superuser


async def get_all_chatbot(current_user: BaseUser):
    check_superuser(current_user)
    return await ChatBot.all()


async def create_chatbot_by_id(current_user: BaseUser, chatbot: ChatBotCreateUpdate):
    check_superuser(current_user)
    return await ChatBot.create(**chatbot.dict())


async def patch_chatbot_by_id(
    id: int, current_user: BaseUser, update_chatbot: ChatBotCreateUpdate
):
    check_superuser(current_user)
    chatbot = await ChatBot.filter(id=id).first()
    if not chatbot:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="chatbot_not_found",
            error="해당 챗봇 프롬프트가 없습니다.",
        )

    chatbot.step = update_chatbot.step
    chatbot.is_terminate = update_chatbot.is_terminate
    chatbot.selection_path = update_chatbot.selection_path
    chatbot.options = update_chatbot.options
    chatbot.answer = update_chatbot.answer
    await chatbot.save()

    return chatbot


async def delete_chatbot_by_id(
    id: int,
    current_user: BaseUser,
):
    check_superuser(current_user)
    chatbot = await ChatBot.filter(id=id).first()
    if not chatbot:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="chatbot_not_found",
            error="해당 챗봇 프롬프트가 없습니다.",
        )
    await chatbot.delete()
