import google.generativeai as genai
import os
import numpy as np

from database.node import EmbeddingNode, FileNode
from config.settings import EMBEDDING_MODEL

class EmbeddingModel:
    def __init__(
            self,
            model_name, 
        ):
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        self.model_name: str = model_name

    async def embed_text(self, text: str) -> np.ndarray:
        embedding = await genai.embed_content(
            model_name=self.model_name,
            content=text
        )
        return embedding

embedding_model = EmbeddingModel(model_name=EMBEDDING_MODEL)

async def embed_file(node: FileNode) -> EmbeddingNode:
    embedding = await embedding_model.embed_text(node.content)
    return EmbeddingNode(
        content_embedding=embedding
    )
    


