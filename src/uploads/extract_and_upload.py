import os

from dotenv import load_dotenv
from src.uploads.extract_notion_pages import extract_notion_pages
from src.uploads.upload_pinecone import upload_pinecone

load_dotenv()
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

notion_pages_texts = extract_notion_pages(NOTION_DATABASE_ID)
print(notion_pages_texts)
upload_pinecone(notion_pages_texts)