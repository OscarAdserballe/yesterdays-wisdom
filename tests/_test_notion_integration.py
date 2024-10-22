from database.data_integrations.notion.notion import get_database, extract_pages
from database.data_integrations.notion.notion_page import NotionPage
from config.config_logger import logger
import pytest
from random import choice

import os

logger.info(os.getcwd())

@pytest.fixture
def database():
    return get_database(
        database_id="beb494e4d3554984a87984e8be8910b8"
    )

def test_notion_pages(database):
    pages = extract_pages(database)
    logger.info(f"Extracted {len(pages)} pages")
    logger.info(choice(pages))
    assert isinstance(choice(pages), NotionPage)
    assert len(pages) > 0
