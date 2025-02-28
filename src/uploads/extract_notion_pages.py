from notion_client import Client
import os

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

notion = Client(auth=NOTION_API_KEY)

def extract_notion_pages(database_id):
    response = notion.databases.query(database_id=database_id)
    extracted_texts = []

    for page in response["results"]:
        page_id = page["id"]
        blocks = notion.blocks.children.list(block_id=page_id)
        for block in blocks["results"]:
            if "type" in block and "rich_text" in block[block["type"]]:
                rich_text_content = block[block["type"]]["rich_text"]

                for text_item in rich_text_content:
                    extracted_texts.append(text_item["text"]["content"].replace("\n", ""))

    return extracted_texts