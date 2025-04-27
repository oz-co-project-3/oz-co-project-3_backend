from app.exceptions.base_exceptions import CustomException


class ChatBotNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="chatbot_not_found", error="챗봇 프롬프트가 없습니다."
        )
