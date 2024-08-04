import requests
from typing import Dict, Optional
from objects import Page
import json
from llm import LLM

INTEGRATION_TOKEN = 'secret_QTLcb31ulTSLdxD12FgmmT1399yxB6YFcO78WEO1zNm'

HEADERS = {
    "Authorization": "Bearer " + INTEGRATION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_database(database_id:str,
                 headers : Dict[str, str]=HEADERS,
                 num_pages : int | float =None
                 ) -> list[Dict]:
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    results = []

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    results.extend(data.get("results", []))
    
    while data.get("has_more") and get_all:
        payload["start_cursor"] = data.get("next_cursor")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        results.extend(data.get("results", []))
    
    return results


def extract_text(raw_text:Dict) -> list[str]:
    KEYS = ["paragraph", "bulleted_list_item", "numbered_list_item", "heading_1", "quote", "image", "code"]
    keys_for_images = ["file", "external"]
    collected_text = []

    for block in raw_text.get("results", []):
        block_type = block.get("type")
        if block_type in KEYS:
            if block_type == "image":
                for image_type in keys_for_images:
                    image_info = block.get(block_type, {}).get(image_type)
                    if image_info:
                        collected_text.append(f"<img src='{image_info['url']}'>")
            else:
                rich_text_items = block.get(block_type, {}).get("rich_text", [])
                for rich_text in rich_text_items:
                    text_content = rich_text.get("text", {}).get("content", "")
                    collected_text.append(text_content)
    merged_text = []
    buffer = ""
    for text in collected_text:
        if buffer and buffer[-1] not in ".?!)]":
            buffer += " " + text
        else:
            if buffer:
                merged_text.append(buffer)
            buffer = text

    if buffer:
        merged_text.append(buffer)

    return merged_text

def fetch_page(page: Page):
    url = f"https://api.notion.com/v1/blocks/{page.id}/children?page_size=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    try:
        page.set_text(extract_text(data))
        return page
    except Exception as e:
        print("Exception {e}")
        return False

def extract_pages(database: list[dict]) -> list[Page]:
    pages = []

    for page_data in database:
        try: 
            page = Page(page_data)
            pages.append(page)
        except AttributeError:
            print(page_data)
            continue

    return pages

def generate_questions(page: Page) -> Optional[Page]:
    flash = LLM("gemini-1.5-flash")
    if page.text != "":
        query = f"""
        Write 5 questions that try to capture the key themes in the following notes - cover the whole text!
         Try to capture through these questions the most abstract and general themes of the notes. The goal is to induce the recollection of the student. But ensure that they are not unanswerable either, of course.

        Also provide brief answers to each of the preceding questions.
        Please provide the response in JSON format of the following form:
        '
        {{
          '1. Some question' : '... some answer to first question',
          ...
          '5. Some fifth question' : '... some answer to fifth question'
        }}
        '
        {page.text}
        """
        output = flash.call_llm(query)
        page.set_questions(response_to_json(output))
        return page
    else:
        raise AttributeError("The page text is empty")


def process_llm_output(llm_output):
    try:
        return str(llm_output.candidates[0].content.parts[0])
    except (AttributeError, IndexError) as e:
        print("Error accessing text content:", e)
        return None

def response_to_json(model_response_text: str) -> dict:
    escaped_json_str = process_llm_output(model_response_text)[16:-7]
    unescaped_str = bytes(escaped_json_str, "utf-8").decode("unicode_escape")
    json_obj = json.loads(unescaped_str)
    return json_obj