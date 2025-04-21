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
                "app.domain.chatbot.model",
                "app.domain.success_review.models",
                "app.domain.free_board.models",
                "app.domain.resume.resume_models",
                "app.domain.comment.models",
                "app.domain.job_posting.job_posting_models",
                "app.domain.user.user_models",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}

# 외부 api
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
