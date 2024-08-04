# llm.py

import google.generativeai as genai
from time import sleep
import json
from src.llm.config_llm import supported_models, default_system_prompts

import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models

import logging

supported_models = {
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.5-pro": "gemini-1.5-pro",
}

default_system_prompts = {
    "gemini-1.5-flash": "",
    "gemini-1.5-pro": "",
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, model_name, system_prompt=None, return_json: bool = False):
        self.return_json = return_json
        if not system_prompt:
            self.system_prompt = self.init_prompt(model_name)
        else:
            self.system_prompt = system_prompt

        # default settings
        self.temperature = 0
        self.max_output_tokens = 4096
        self.top_p = 1
        self.generation_config = {
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }
        self.safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        }
        if self.return_json:
            self.generation_config.update({"response_mime_type": "application/json"})

        self.model, self.custom_model = self.init_model(
            model_name
        )  # fine-tuned models will need to be called throug hteh vertex ai platform

        self.log_output = False  # functionality to be defined: just a placeholder, but in the future just pushing all output to BQ or something.

    def init_model(self, model_name: str):
        model_id = supported_models[model_name]
        if "projects" in model_id:
            vertexai.init(project="874637833154", location="europe-west1")
            model = GenerativeModel(
                model_id,
                system_instruction=[self.system_prompt],
            )
            return model, True
        else:
            model = genai.GenerativeModel(
                model_id, system_instruction=self.system_prompt
            )
            return model, False

    def init_prompt(self, model_name: str):
        return default_system_prompts[model_name]

    async def call_async_llm(self, input_text: str):
        if self.custom_model:
            self.chat = self.model.start_chat(response_validation=False)
            output = self.chat.send_message(
                input_text,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
            )
            response = output.text
        else:
            response = self.model.generate_content(input_text).text

        if self.return_json:
            return self.response_to_json(response)
        else:
            return response

    def call_llm(self, input_text: str):
        if self.custom_model:
            self.chat = self.model.start_chat(response_validation=False)
            output = self.chat.send_message(
                input_text,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
            )
            response = output.text
        else:
            response = self.model.generate_content(input_text).text

        if self.return_json:
            return self.response_to_json(response)
        else:
            return response

    # note: does not support custom models
    def stream_response(self, input_text: str):
        buffer_size: int = 20
        sleep_time: float = 0.03

        response = self.model.generate_content(input_text, stream=True)
        buffer = ""
        for chunk in response:
            buffer += chunk.text
            while len(buffer) >= buffer_size:
                yield buffer[:buffer_size]
                buffer = buffer[buffer_size:]
                sleep(sleep_time)
        if buffer:
            yield buffer

    def response_to_json(self, model_response_text: str) -> dict:
        try:
            return json.loads(
                model_response_text.replace("json", "").replace("```", "")
            )
        except Exception:
            return {"error": "Could not parse JSON \n {e}"}

    def get_model_input(self, input_text: str) -> str:
        return f"""
        {self.system_prompt}:
        {input_text}
        """
