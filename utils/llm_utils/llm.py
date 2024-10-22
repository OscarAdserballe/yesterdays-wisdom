import google.generativeai as genai
import os
import json

from llm_utils.prompts.prompts import PROMPTS
from config.config_logger import get_logger, LOG_DELIMITER
class LLM:
    def __init__(
        self,
        model_name,
        system_prompt=None,
        return_json: bool = False,
        cache_prompt: bool = False,
        log_output: bool = True,
    ):
        """
        Initializes the LLM object with configuration settings.

        Parameters:
        model_name (str): The name of the model to use.
        system_prompt (str, optional): The system prompt to use. Defaults to None.
        return_json (bool, optional): Whether to return the output as JSON. Defaults to False.
        log_output (bool, optional): Whether to log the output. Defaults to True.
        """
        self.return_json = return_json
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

        self.model, self.custom_model = self.init_model(model_name)
        self.log_output = log_output

    def init_model(self, model_name: str):
        """
        Initializes the model based on the provided model name.

        Parameters:
        model_name (str): The name of the model to initialize.

        Returns:
        tuple: A tuple containing the model and a boolean indicating if it's a custom model.
        """
        model_id = supported_models[model_name]
        custom_model = True if "projects" in model_id else False

        kwargs = {}
        if self.system_prompt is not None:
            if custom_model:
                kwargs["system_instruction"] = [self.system_prompt]
            else:
                kwargs["system_instruction"] = self.system_prompt

        if custom_model:
            logging.debug(f"Using model {model_id}")
            vertexai.init(project="874637833154", location="europe-west1")
            model = GenerativeModel(model_id, **kwargs)
        else:
            credentials = service_account.Credentials.from_service_account_file(
                "credentials/gcp.json"
            )
            genai.configure(credentials=credentials)
            model = genai.GenerativeModel(model_id, **kwargs)
        return model, custom_model

    @log_output_to_bigquery
    async def call_async_llm(self, input_text: str):
        """
        Asynchronously calls the language model with the provided input text.

        Parameters:
        input_text (str): The input text to process.

        Returns:
        str or dict: The response from the model, either as a string or JSON.
        """
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

    @log_output_to_bigquery
    def call_llm(self, input_text: str):
        """
        Calls the language model with the provided input text.

        Parameters:
        input_text (str): The input text to process.

        Returns:
        str or dict: The response from the model, either as a string or JSON.
        """
        if self.custom_model:
            self.chat = self.model.start_chat(response_validation=False)
            output = self.chat.send_message(
                input_text,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
            )
            response = output.text
        else:
            try: response = self.model.generate_content(input_text).text
            except ValueError: return "Safety settings banned output..."
            except Exception as e: raise
        if self.return_json:
            return self.response_to_json(response)
        else:
            return response

    # Generators difficult to log. WIP.
    def stream_response(self, input_text: str):
        """
        Streams the response from the model for the provided input text.

        Parameters:
        input_text (str): The input text to process.

        Yields:
        str: Chunks of the response text.
        """
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
        """
        Converts the model response text to a JSON object.

        Parameters:
        model_response_text (str): The response text from the model.

        Returns:
        dict: The JSON representation of the response text.
        """
        # cleaning json string
        model_response_text = model_response_text.replace("```", "")
        model_response_text = re.sub(
            r"\n|\t|\r", "", model_response_text
        )  # Remove escaped newlines, tabs, etc.
        model_response_text = re.sub(
            r"json", "", model_response_text, flags=re.IGNORECASE
        )  # Remove 'json' keyword
        model_response_text = model_response_text.strip()

        try:
            return json.loads(model_response_text)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON response",
                "response": model_response_text,
            }
        except Exception as e:
            return {
                "error": f"An error occurred: {str(e)}",
                "response": model_response_text,
            }

    def get_model_input(self, input_text: str) -> str:
        """
        Formats the input text with the system prompt.

        Parameters:
        input_text (str): The input text to format.

        Returns:
        str: The formatted input text.
        """
        return f"""
        {self.system_prompt}:
        {input_text}
        """
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

