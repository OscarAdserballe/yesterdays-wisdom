from objects.node import (
    Node,
    NODE_PROPERTIES
)
from typing import Optional, List

def get_content_metadata(node: Node) -> Node:
    field_definitions = {
        property.name: (property.description, property.datatype)
        for property in NODE_PROPERTIES if property.llm_task
    }
    current_node_properties = node.__repr__

    query = f"""
    Get the following information about the given piece of content based on the exisitng information.

    Here are the fields you should extract in JSON format along with a brief description:
    <fields>
        {field_definitions}
    </fields>


    Here is the current information about the Node object.
    Most of your guess should probably be derived from the text content of the node, but maybe there'll be hints in the other fields as well:
    <current_node>
        {current_node_properties}
    </current_node>
    """

def process_llm_output(llm_output):
    try:
        return str(llm_output.candidates[0].content.parts[0])
    except (AttributeError, IndexError) as e:
        print("Error accessing text content:", e)
        return None

def response_to_json(model_response_text: str) -> dict:
    escaped_json_str = process_llm_output(model_response_text)[16:-7]
    unescaped_str = bytes(escaped_json_str, "utf-8").decode("unicode_escape")
    json_obj = json.loads(unescaped_str)
    return json_obj