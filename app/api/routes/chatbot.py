from typing import List

from fastapi import APIRouter, Depends, status

from app.core.token import get_current_user
from app.models.user_models import BaseUser
from app.schemas.chatbot_schemas import ChatBotCreateUpdate, ChatBotResponseSchema
from app.services.chatbot_services import (
    create_chatbot_by_id,
    delete_chatbot_by_id,
    get_all_chatbot,
    patch_chatbot_by_id,
)

chatbot_router = APIRouter(prefix="/api/admin/chatbot", tags=["chatbot"])


@chatbot_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="챗봇 프롬프트 생성",
    description=(
        """
    - `400` `code`:`required_field` 필수 필드 누락\n
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    - `403` `code`:`permission_denied` 권한이 없습니다.\n
    """
    ),
)
async def create_chatbot(
    chatbot: ChatBotCreateUpdate, current_user: BaseUser = Depends(get_current_user)
):
    return await create_chatbot_by_id(current_user, chatbot)


@chatbot_router.get(
    "/",
    response_model=List[ChatBotResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="챗봇 프롬프트 조회",
    description=(
        """
    - `400` `code`:`required_field` 필수 필드 누락\n
    - `401` `code`:`auth_required` 인증이 필요합니다.\n
    - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
    - `403` `code`:`permission_denied` 권한이 없습니다.\n
    """
    ),
)
async def get_list_chatbots(current_user: BaseUser = Depends(get_current_user)):
    return await get_all_chatbot(current_user)


@chatbot_router.patch(
    "/{id}/",
    response_model=ChatBotResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="챗봇 프롬프트 수정",
    description=(
        """
        - `400` `code`:`required_field` 필수 필드 누락\n
        - `401` `code`:`auth_required` 인증이 필요합니다.\n
        - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
        - `403` `code`:`permission_denied` 권한이 없습니다.\n
        - `404` `code`:`chatbot_not_found` 챗봇 프롬프트가 없습니다.\n
        """
    ),
)
async def patch_chatbot(
    id: int,
    chatbot: ChatBotCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
):
    return await patch_chatbot_by_id(id, current_user, chatbot)


@chatbot_router.delete(
    "/{id}/",
    status_code=status.HTTP_200_OK,
    summary="챗봇 프롬프트 삭제",
    description=(
        """
        - `400` `code`:`required_field` 필수 필드 누락\n
        - `401` `code`:`auth_required` 인증이 필요합니다.\n
        - `401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
        - `403` `code`:`permission_denied` 권한이 없습니다.\n
        - `404` `code`:`chatbot_not_found` 챗봇 프롬프트가 없습니다.\n
        """
    ),
)
async def delete_chatbot(
    id: int,
    current_user: BaseUser = Depends(get_current_user),
):
    await delete_chatbot_by_id(id, current_user)
    return {"message": "프롬프트가 삭자되었습니다."}
