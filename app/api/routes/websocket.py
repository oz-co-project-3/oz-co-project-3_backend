from fastapi import APIRouter, WebSocket

from app.models.chatbot_model import ChatBot
from app.utils.exception import CustomException

websocket_router = APIRouter(
    prefix="/api/ws",
    tags=["websocket"],
)


@websocket_router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    selected = []
    while True:
        message = await websocket.receive_text()
        selected.append(message)
        path = "/".join(selected)
        chatbot_response = await ChatBot.filter(selection_path=path).first()

        if not chatbot_response:
            await websocket.send_json(
                {"code": "path_not_found", "error": "경로에 없는 선택지입니다."}
            )
            selected.pop()  # 루프 돌리기
            continue

        if chatbot_response.is_terminate:
            await websocket.send_json(
                {
                    "step": chatbot_response.step,
                    "selection_path": chatbot_response.selection_path,
                    "answer": chatbot_response.answer,
                    "options": chatbot_response.options,
                    "is_terminate": chatbot_response.is_terminate,
                }
            )
            await websocket.close()
            break

        await websocket.send_json(
            {
                "step": chatbot_response.step,
                "selection_path": chatbot_response.selection_path,
                "answer": chatbot_response.answer,
                "options": chatbot_response.options,
                "is_terminate": chatbot_response.is_terminate,
            }
        )
