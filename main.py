from components.transcribe_notes.transcribe_notes.config_categorization import CATEGORIZE_PROMPT
from components.transcribe_notes.get_notes import create_notes_objects
from components.transcribe_notes.objects import Class, Topic

import PIL.Image
import random
import subprocess

from pydantic_ai import Agent

LLM_MODEL = "gemini-1.5-flash"

def get_topics(agent: Agent, some_class: Class) -> Class:
    """
    Categorize notes into topics using PydanticAI and update the Class object.
    """
    # Prepare image data
    image_data = []
    for note in some_class.notes:
        encoded_img = encode_image(note.path)
        image_data.append({
            "file_name": note.file_name,
            "image_base64": encoded_img
        })

    # Create the prompt with examples
    prompt = CATEGORIZE_PROMPT + "\n" + str(image_data)

    # Call the LLM
    response = agent.run_sync(prompt)

    # Parse the response into Topic objects
    topics = []
    for topic_data in response.data:
        topic = Topic(
            topic_name=topic_data["topic"],
            pages=[Path(page) for page in topic_data["pages"]],
            description=topic_data["description"],
            content=""  # To be filled in transcription step
        )
        topics.append(topic)
    
    # Attach topics to the class
    some_class.topics = {topic.topic_name: [str(page) for page in topic.pages] for topic in topics}
    
    return some_class

agent = Agent(
    model_name=LLM_MODEL,
    system_prompt="""
    You are an assistant that transcribes notes from images, categorizes them into topics, and structures the data accordingly.
    """
)

def main():
    # Path to your notes
    notes_path = Path('path/to/your/NOTES_PATH')

    # Create class and note objects
    classes = create_notes_objects(notes_path)

    # Iterate through each class
    for some_class in classes:
        print(f"Processing class: {some_class.class_name}")

        # Categorize notes into topics
        categorized_class = get_topics(agent, some_class)

        # Iterate through each topic
        for topic in categorized_class.topics.values():
            print(f"Transcribing topic: {topic.topic_name}")

            # Transcribe the topic
            transcribed_topic = transcribe_topic(agent, topic)

            # Save to Obsidian
            output_file = save_to_obsidian(transcribed_topic, some_class.class_name, Path('path/to/Obsidian/Vault'))
            print(f"Saved to: {output_file}")

if __name__ == "__main__":
    main()
