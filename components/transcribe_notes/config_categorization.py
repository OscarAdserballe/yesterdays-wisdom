from pydantic import BaseModel, Field

class Class(BaseModel):
    notes: 
CATEGORIZE_PROMPT = """
You will be categorizing a number of notes into appropriate content.
Currently, the problem is that the notes are scattered after an upload process, and you need to identify the pages that belong together based on the topics they revolve around.

The order in which you receive the notes can sometimes be informative, but it should not be taken as a given.
The minimum unit we're working with is a single page per topic, but a topic can span multiple pages.

You will be provided with a set of notes in the form of images, one per page, along with some metadata.
When citing the pages, it should always be in terms of their filenames.

The output format should be a list of JSON object as follows:
Topic = {
    "topic": str,
    "pages": List[str],
    "description": str
}
And then the final output should be List[Topic]

Here are the notes you need to categorize:
"""
