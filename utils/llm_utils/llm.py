import google.generativeai as genai
import os
import json

from llm_utils.prompts.prompts import PROMPTS
from config.config_logger import get_logger, LOG_DELIMITER

class BaseLLM:
    def __init__(
            self,
            model_name: str="gemini-1.5-flash",
            system_prompt: str=PROMPTS["default"],
            temperature: float=0.5,
            response_mime_type = "text/plain",
            max_output_tokens = "8000",
            log=True,
            
        ):
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.generation_config = genai.GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            response_mime_type=response_mime_type

        )
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt
        )
        self.log = log

        if self.log: self.logger = get_logger(__name__)

    def parse_shitty_response(self, response):
        return response.candidates[0].content.parts[0].text

    def query(self, query: str, context: str=""):
        prompt = f"""
        Query: {query}
        
        Context Documents: {context}
        """
        response = self.model.generate_content(prompt)
        try:
            answer = response.text
        except:
            answer = self.parse_shitty_response(response)
        
        if self.log: self.logger.info(f"{LOG_DELIMITER} Query: {query}\n\n\nAnswer: {answer}\n\n\n\n\n\n")
        return answer

