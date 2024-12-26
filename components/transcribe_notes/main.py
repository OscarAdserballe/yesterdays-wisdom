from transcribe_notes.config_transcription import TRANSCRIPTION_PROMPT, IMAGE_EXAMPLES
from transcribe_notes.config_categorization import CATEGORIZE_PROMPT
from transcribe_notes.get_notes import create_notes_pageects 
from utils.objects import Class, Note, Topic

import PIL.Image
import random
import subprocess

# General flow: Images in class-folders
# -> define class as selection of topics rather than pages (get_topics)
# -> transcribe set of topics (transcribe_topic)
     
def get_topics(some_class: Class):
    flash = LLM(
        model_name=LLM_MODEL,
        system_prompt=CATEGORIZE_PROMPT,
        return_json=True
    )

    # For each class, upload entire set of notes and get the topics contained with the one llm call.
    for j, page in enumerate(some_class.notes):
        flash.add_file(
            file_path=page.path,
            file_name=page.file_name
        )

    output = flash.call_llm(CATEGORIZE_PROMPT)
    flash.delete_files()

    class_topics = []
    for topic in output:
        class_topics.append(
            Topic(
                topic_name = topic.get("topic"),
                pages = topic.get("pages"),
                description = topic.get("description")
            )
        )

    return some_class


def transcribe_topic(topic: Topic):
    flash = LLM(
        model_name=LLM_MODEL,
        system_prompt=TRANSCRIPTION_PROMPT,
        return_json=True
    )

    topic_images = []

    for i, page in topic.pages:
        img = PIL.Image.open(page.path)
        topic_images.append(img)

        print(page.path)
        print(f"Transcribing {page.file_name}...")

        flash.add_file(
            file_path=page.path,
            file_name=page.file_name,
        )

    output = flash.call_llm(IMAGE_EXAMPLES + topic_images + ["Transcribe these pages to the best of your ability"])

    ### SOMETHIGN ###
    topic.transcription = output.get("transcription")
    topic.keywords = output.get("keywords")

    return topic
