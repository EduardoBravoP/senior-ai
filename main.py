from dotenv import load_dotenv
import os
from extract_notion_pages import extract_notion_pages

load_dotenv()

NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

notion_pages = extract_notion_pages(NOTION_DATABASE_ID)

print(notion_pages)