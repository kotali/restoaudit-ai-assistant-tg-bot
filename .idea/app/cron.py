# api/cron.py
from fastapi import Response
import asyncio
from rag_loader import load_index
from scripts.generate_docs import update_notion

async def run():
    update_notion()
    await load_index()

def handler(request):
    asyncio.run(run())
    return Response(content="Cron OK", media_type="text/plain")