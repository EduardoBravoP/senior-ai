from notion_client import Client
import os

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
notion = Client(auth=NOTION_API_KEY)

def extract_notion_pages(database_id):
    response = notion.databases.query(database_id=database_id)
    extracted_texts = []

    for page in response["results"]:
        page_id = page["id"]
        page_contents = []
        blocks = notion.blocks.children.list(block_id=page_id)
        
        numbered_list_counter = 1  # Contador para listas numeradas

        for block in blocks["results"]:
            if "type" in block and "rich_text" in block[block["type"]]:
                rich_text_content = block[block["type"]]["rich_text"]
                
                text_content = "".join(text_item["text"]["content"] for text_item in rich_text_content)

                # Se for um item de lista numerada, adiciona o número manualmente
                if block["type"] == "numbered_list_item":
                    text_content = f"{numbered_list_counter}. {text_content}"
                    numbered_list_counter += 1  # Incrementa o contador
                else:
                    numbered_list_counter = 1  # Reseta o contador se não for lista numerada

                page_contents.append(text_content)

        extracted_texts.append(" ".join(page_contents))

    return extracted_texts
