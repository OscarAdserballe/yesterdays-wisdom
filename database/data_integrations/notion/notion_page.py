from typing import Dict
import requests

from database.data_integrations.notion.notion_config import HEADERS
from config.config_logger import logger

class NotionPage:
    def __init__(
            self, page_data:Dict
        ):
        self.id = page_data.get("id")
        self.created_time = page_data.get("created_time")
        self.last_edited_time = page_data.get("last_edited_time")
        self.created_by = page_data.get("created_by", {}).get("id")
        self.url = page_data.get("url")
        self.public_url = page_data.get("public_url")
        
        self.properties = page_data.get("properties", {})
        self.text = self.fetch_text()

        try: self.title = self.properties.get('Name').get('title')[0].get('text').get('content')
        except: self.title = ''
        
        try: self.type = self.properties.get('Type').get('select').get('name')
        except: self.type = ''

        try: self.in_class = self.properties.get('Class').get('multi_select')[0].get('name')
        except: self.in_class = ""
        

    def __repr__(self):
        return f"Page(id={self.id}) (title={self.title}) (type={self.type})"

    
    def fetch_text(self):
        url = f"https://api.notion.com/v1/blocks/{self.id}/children?page_size=100"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        try:
            return self.extract_text(data)
        except Exception as e:
            logger.exception("Exception {e}")
    
    @staticmethod
    def extract_text(raw_text:Dict) -> list[str]:
        KEYS = [
            "paragraph", "bulleted_list_item", "numbered_list_item", "heading_1", "quote", "image", "code"
        ]
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
    
    