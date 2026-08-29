from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

from app.agent import AgentNotConfigured, AgentRequestError, HealthAgent
from app.config import Settings, get_settings
from app.garmin.client import GarminDataAccess
from app.storage import HealthCache
from app.telegram import TelegramClient, extract_text_message


def create_app(settings: Settings | None = None, agent: HealthAgent | None = None) -> FastAPI:
    settings = settings or get_settings()
    cache = HealthCache(settings.database_path)
    data_access = GarminDataAccess(cache)
    runtime_agent = agent or HealthAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        data_access=data_access,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield

    app = FastAPI(title="Health Assistant", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.agent = runtime_agent

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/telegram/webhook")
    async def telegram_webhook(
        request: Request,
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ) -> dict[str, str]:
        configured_secret = settings.telegram_webhook_secret
        if configured_secret and x_telegram_bot_api_secret_token != configured_secret:
            raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

        update: dict[str, Any] = await request.json()
        message = extract_text_message(update)
        if message is None:
            return {"status": "ignored"}

        chat_id, text = message
        if settings.telegram_allowed_chat_id is not None and chat_id != settings.telegram_allowed_chat_id:
            raise HTTPException(status_code=403, detail="Unauthorized Telegram chat")

        try:
            answer = runtime_agent.answer(text)
        except AgentNotConfigured:
            answer = "The health assistant is not configured with a model API key yet."
        except (AgentRequestError, RuntimeError, ValueError):
            answer = "I could not process that request. Check the server logs."

        if settings.telegram_bot_token:
            await TelegramClient(settings.telegram_bot_token).send_message(chat_id=chat_id, text=answer)
        return {"status": "ok"}

    return app


app = create_app()
