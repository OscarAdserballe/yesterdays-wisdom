from database.data_integrations.onedrive_files.local_files import FileParser
from config.config_logger import logger

import pytest
import os

logger.info(os.getcwd())

@pytest.fixture
def database():
    LOCAL_FILES_PATH = "/Users/oscarjuliusadserballe/OneDrive"
    PARSED_FILES_PATH = "/Users/oscarjuliusadserballe/OneDrive/5th Semester/Yesterdays Wisdom/cache_files"
    
    file_parser = FileParser(LOCAL_FILES_PATH, PARSED_FILES_PATH)
    processed_nodes = file_parser.run()
    return processed_nodes

def test_local_files(database):
    assert database is not None
