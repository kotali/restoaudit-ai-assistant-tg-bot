from fastapi import FastAPI, Request
from bot import dp, bot  # Импорт из bot.py
import asyncio
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    # Обработка webhook от Telegram
    await dp.feed_update(bot, update)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)