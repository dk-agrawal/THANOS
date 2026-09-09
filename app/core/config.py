import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    APP_NAME = os.getenv(
        "APP_NAME",
        "THANOS",
    )

    APP_ENV = os.getenv(
        "APP_ENV",
        "development",
    )

    # AI
    AI_PROVIDER = os.getenv(
        "AI_PROVIDER",
        "",
    )

    AI_MODEL = os.getenv(
        "AI_MODEL",
        "openai/gpt-4o-mini-2024-07-18",
    )

    # API KEYS
    OPENROUTER_API_KEY = os.getenv(
        "OPENROUTER_API_KEY",
        "",
    )

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY",
        "",
    )

    NEWS_API_KEY = os.getenv(
        "NEWS_API_KEY",
        "",
    )

    GITHUB_TOKEN = os.getenv(
        "GITHUB_TOKEN",
        "",
    )

    # THANOS UPDATE
    GITHUB_OWNER = os.getenv(
        "GITHUB_OWNER",
        "",
    )

    GITHUB_REPO = os.getenv(
        "GITHUB_REPO",
        "",
    )

    PROJECT_ROOT = os.getenv(
        "PROJECT_ROOT",
        ".",
    )

    # API BASE URLs
    OPENROUTER_BASE_URL = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )

    NEWS_API_BASE_URL = os.getenv(
        "NEWS_API_BASE_URL",
        "https://newsapi.org/v2",
    )

    GITHUB_API_BASE_URL = os.getenv(
        "GITHUB_API_BASE_URL",
        "https://api.github.com",
    )


settings = Settings()