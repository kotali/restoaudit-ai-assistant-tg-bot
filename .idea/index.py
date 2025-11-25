from fastapi import FastAPI, Request
from aiogram import Bot  # Импорт твоего dp и bot
import asyncio

app = FastAPI()  # Обязательно!

@app.post("/webhook")  # POST для Telegram updates
async def webhook(request: Request):
    update = await request.json()
    await dp.feed_update(bot, update)  # Обработка
    return {"status": "ok"}

# Для теста: GET на корень
@app.get("/")
async def root():
    return {"message": "Bot is alive! Use /webhook for Telegram."}

# Vercel ожидает это для Python
def handler(request):
    return app(request)  # Или используй uvicorn, но Vercel сам запустит