import os
from pathlib import Path

from dotenv import load_dotenv

ENV = os.getenv("ENV", "dev")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / f".envs/.{ENV}.env"

load_dotenv(dotenv_path=ENV_PATH)

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

POSTGRES_URL = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URL},
    "apps": {
        "models": {
            "models": [
                "app.models.chatbot_model",
                "app.models.success_review_models",
                "app.models.free_board_models",
                "app.models.resume_models",
                "app.models.comment_models",
                "app.models.job_posting_models",
                "app.models.user_models",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}
