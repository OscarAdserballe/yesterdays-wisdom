from config.config_logger import logger
from database.local_files_walker.local_files import FileParser 
from config.settings import LOCAL_FILES_PATH, PARSED_FILES_PATH 

import pytest
import os

logger.info(os.getcwd())

@pytest.fixture
def database():
    file_parser = FileParser(LOCAL_FILES_PATH, PARSED_FILES_PATH)
    processed_nodes = file_parser.run()
    return processed_nodes

def test_local_files(database):
    assert database is not None
