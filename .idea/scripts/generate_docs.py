import os
from notion_client import Client
from datetime import datetime
import mkdocs
from mkdocstrings import Collector
import inspect
from bot import handle_message  # Пример импорта функции для docstrings

notion = Client(auth=os.getenv("NOTION_TOKEN"))
page_id = os.getenv("NOTION_PAGE_ID")

def generate_notion_docs():
    # Пример извлечения docstring
    docstring = inspect.getdoc(handle_message)

    # Блоки для Notion
    blocks = [
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": f"Bot Docs (обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M')} )"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Описание: Telegram-бот с RAG для ERP-услуг."}}]}
        },
        {
            "object": "block",
            "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": docstring or "Добавь docstring в bot.py"}}], "language": "python"}
        },
        # Добавь больше: API, RAG-setup и т.д.
    ]

    notion.blocks.children.append(page_id, children=blocks)
    print("Docs updated in Notion!")

if __name__ == "__main__":
    generate_notion_docs()