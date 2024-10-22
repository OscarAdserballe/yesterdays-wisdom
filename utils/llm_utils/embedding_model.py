import google.generativeai as genai
import os
import numpy as np

class EmbeddingModel:
    def __init__(
            self,
            model_name: str = "models/text-embedding-004", 
        ):
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        """ Initializes the EmbeddingModel with a specific model name and credentials. """
        self.model_name: str = model_name

    def embed_text(self, text: str) -> np.array
        """ Embeds text using the model. """
        return genai.embed_content(
            model_name=self.model_name,
            content=text
        )
        