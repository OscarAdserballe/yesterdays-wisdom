from config.config_logger import logger
from config.settings import LOCAL_FILES_PATH, PARSED_FILES_PATH 

from components.local_files_walker.local_files import FileParser 
from components.featurisation.llm_agent import file_node_to_llm_node
from components.featurisation.embedding_model import embed_file

import os
import asyncio

if __name__ == "__main__":
    logger.info(os.getcwd())
    ### Parsing local files
    file_parser = FileParser(LOCAL_FILES_PATH, PARSED_FILES_PATH)
    processed_file_nodes = file_parser.run()
    
    print(f"Parsed {len(processed_file_nodes)} files")
    # for each node, pass through and create LLMNode and EmbeddingNode
    # for file_node in processed_file_nodes:
    #     llm_node = await file_node_to_llm_node(file_node)
    #     embedding_node = await embed_file(file_node)
    #     result = asyncio.gather(*(#placehodler))
    #     node = Node(
    #         file=file_node,
    #         llm=llm_node,
    #         embedding=embedding_node
    #     )
    #
    #     # TO COMPLETE
    #     push_node_to_db(node)
#

