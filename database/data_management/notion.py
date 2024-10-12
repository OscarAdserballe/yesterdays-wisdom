import requests
from typing import Dict, Optional, List
from objects import Page
import json
from llm import LLM
from dotenv import load_dotenv
import os

INTEGRATION_TOKEN = os.getenv('INTEGRATION_TOKEN')

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

class NotionPage:
    def __init__(self, page_data:Dict):
        self.id = page_data.get("id")
        self.created_time = page_data.get("created_time")
        self.last_edited_time = page_data.get("last_edited_time")
        self.created_by = page_data.get("created_by", {}).get("id")
        self.url = page_data.get("url")
        self.public_url = page_data.get("public_url")
        
        self.properties = page_data.get("properties", {})

        try: self.title = self.properties.get('Name').get('title')[0].get('text').get('content')
        except: self.title = ''
        
        try: self.type = self.properties.get('Type').get('select').get('name')
        except: self.type = ''

        try: self.in_class = self.properties.get('Class').get('multi_select')[0].get('name')
        except: self.in_class = ""
        
        self.text = ""
        self.questions = ""

    def __repr__(self):
        return f"Page(id={self.id}) (title={self.title}) (type={self.type})"

    def set_text(self, text:str):
        self.text = text

    def set_questions(self, questions:str):
        self.questions = questions

def extract_pages(database:list[Dict]) -> list[NotionPage]:
    pages = []

    for page_data in database:
        try: 
            page = NotionPage(page_data)
            pages.append(page)
        except AttributeError:
            print(page_data)
            continue

    return pages

class Note:
    def __init__(self, path:str,
                 file_name:str, class_name:str):
        self.file_name = file_name
        self.path = path
        self.class_name = class_name
        self.topic = None
        self.content = None

class Topic:
    def __init__(self,
                 topic_name:str,
                 pages: List[str],
                 description: str,
                 ):
        self.topic_name = topic_name
        self.pages = pages
        self.description = description

        self.keywords = []
        self.transcription = None