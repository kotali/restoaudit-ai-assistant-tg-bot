import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding  # или другой
from chromadb import PersistentClient
import openai  # или anthropic

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Инициализация RAG
chroma_client = PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("erp_knowledge")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
embed_model = OpenAIEmbedding()

# Загрузка/обновление индекса (вызывать при старте или по cron)
async def load_index():
    if not os.path.exists("./data"):
        os.makedirs("./data")
    # Загружаем файлы из /data
    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)
    return index

index = asyncio.run(load_index())  # Загружаем при старте

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я бот по ERP-услугам. Задавай вопросы по договору, PDF или перепискам.")

@dp.message()
async def handle_message(message: Message):
    query = message.text
    # RAG-запрос
    retriever = index.as_retriever()
    nodes = retriever.retrieve(query)
    context = "\n".join([node.text for node in nodes])

    # Промпт под твою услугу
    prompt = f"""Ты эксперт по внедрению ERP. Отвечай только по предоставленным документам. Если не уверен — скажи 'Уточню у менеджера'.
    Контекст: {context}
    Вопрос: {query}"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )
    answer = response.choices[0].message.content

    await message.answer(answer)

    # Авто-сохранение переписки в базу (для обновления знаний)
    with open("./data/chats.txt", "a", encoding="utf-8") as f:
        f.write(f"Q: {query}\nA: {answer}\n\n")
    # Переиндексация после сохранения (опционально, для cron)
    index = await load_index()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())