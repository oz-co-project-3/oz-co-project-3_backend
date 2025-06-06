import logging
from typing import List

from fastapi import APIRouter, Depends, Path, status

from app.core.token import get_current_user
from app.domain.chatbot.schemas import ChatBotCreateUpdate, ChatBotResponseDTO
from app.domain.chatbot.services import (
    create_chatbot_by_id_service,
    delete_chatbot_by_id_service,
    get_all_chatbots_service,
    patch_chatbot_by_id_service,
)
from app.domain.user.models import BaseUser

logger = logging.getLogger(__name__)

chatbot_router = APIRouter(prefix="/api/admin/chatbot", tags=["chatbot"])


@chatbot_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatBotResponseDTO,
    summary="챗봇 프롬프트 생성",
    description=(
        """
`400` `code`:`required_field` 필수 필드 누락\n
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다.\n
`422` : Unprocessable Entity
    """
    ),
)
async def create_chatbot(
    chatbot: ChatBotCreateUpdate, current_user: BaseUser = Depends(get_current_user)
):
    logger.info(f"[API] 관리자 챗봇 프롬프트 생성 요청: 관리자_id={current_user.id}")
    return await create_chatbot_by_id_service(current_user, chatbot)


@chatbot_router.get(
    "/",
    response_model=List[ChatBotResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="챗봇 프롬프트 조회",
    description=(
        """
`400` `code`:`required_field` 필수 필드 누락\n
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다.\n
    """
    ),
)
async def get_list_chatbots(current_user: BaseUser = Depends(get_current_user)):
    logger.info(f"[API] 관리자 챗봇 프롬프트 전체 조회 요청: 관리자_id={current_user.id}")
    return await get_all_chatbots_service(current_user)


@chatbot_router.patch(
    "/{id}/",
    response_model=ChatBotResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="챗봇 프롬프트 수정",
    description=(
        """
`400` `code`:`required_field` 필수 필드 누락\n
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다.\n
`404` `code`:`chatbot_not_found` 챗봇 프롬프트가 없습니다.\n
`422` : Unprocessable Entity
        """
    ),
)
async def patch_chatbot(
    chatbot: ChatBotCreateUpdate,
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(..., gt=0, le=2147483647, description="chatbot ID (1 ~ 2147483647)"),
):
    logger.info(f"[API] 관리자 챗봇 프롬프트 수정 요청: 관리자_id={current_user.id}, chatbot_id={id}")
    return await patch_chatbot_by_id_service(id, current_user, chatbot)


@chatbot_router.delete(
    "/{id}/",
    status_code=status.HTTP_200_OK,
    summary="챗봇 프롬프트 삭제",
    description=(
        """
`400` `code`:`required_field` 필수 필드 누락\n
`401` `code`:`auth_required` 인증이 필요합니다.\n
`401` `code`:`invalid_token` 유효하지 않은 토큰입니다.\n
`403` `code`:`permission_denied` 권한이 없습니다.\n
`404` `code`:`chatbot_not_found` 챗봇 프롬프트가 없습니다.\n
`422` : Unprocessable Entity
"""
    ),
)
async def delete_chatbot(
    current_user: BaseUser = Depends(get_current_user),
    id: int = Path(..., gt=0, le=2147483647, description="chatbot ID (1 ~ 2147483647)"),
):
    logger.info(f"[API] 관리자 챗봇 프롬프트 삭제 요청: 관리자_id={current_user.id}, chatbot_id={id}")
    await delete_chatbot_by_id_service(id, current_user)
    return {"message": "프롬프트가 삭제되었습니다."}
