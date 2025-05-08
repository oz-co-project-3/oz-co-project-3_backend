from app.core.settings import settings

POSTGRES_URL = f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URL},
    "apps": {
        "models": {
            "models": [
                "app.domain.chatbot.model",
                "app.domain.success_review.models",
                "app.domain.free_board.models",
                "app.domain.resume.models",
                "app.domain.comment.models",
                "app.domain.job_posting.models",
                "app.domain.user.models",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}
