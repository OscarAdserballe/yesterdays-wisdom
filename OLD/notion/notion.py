import requests
from typing import Dict

from database.data_integrations.notion.notion_page import NotionPage
from database.data_integrations.notion.notion_config import HEADERS, INTEGRATION_TOKEN
from config.config_logger import logger

def get_database(
        database_id:str,
        headers : Dict[str, str]=HEADERS,
        num_pages : int | float =None
                 ) -> list[Dict]:
    """Fetches all pages from a Notion database.

    Args:
        database_id (str): The ID of the Notion database to fetch.
        headers (Dict[str, str], optional): The headers to use for the request. Defaults to HEADERS.
        num_pages (int | float, optional): The number of pages to fetch. If None, fetches all pages. Defaults to None.

    Returns:
        list[Dict]: A list of dictionaries, each representing a page in the database.
    """
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

def extract_pages(
        database:list[Dict]
    ) -> list[NotionPage]:
    """Extracts NotionPage objects from a database.

    Args:
        database (list[Dict]): A list of dictionaries, each representing a page in the database.

    Returns:
        list[NotionPage]: A list of NotionPage objects.
    """
    pages = []

    for page_data in database:
        try: 
            page = NotionPage(page_data)
            pages.append(page)
        except AttributeError:
            logger.exception(f"Error extracting page: {page_data}, skipping...")
            continue

    return pages


