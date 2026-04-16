import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram(message: str, token: str = None, chat_id: str = None):
    if not token:
        token = TELEGRAM_BOT_TOKEN
    if not chat_id:
        chat_id = TELEGRAM_CHAT_ID

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")

def format_agent_result(agent_id, status, details):
    return f"<b>Агент:</b> {agent_id}\n<b>Статус:</b> {status}\n<b>Детали:</b> {details}"
