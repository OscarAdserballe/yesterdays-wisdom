from typing import List
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NodeProperty:
    _instances = []

    def __init__(self,
                 name: str,
                 datatype: str,
                 description: str,
                 restricted_to: Optional[List[str]] = None,
                 mode: str = "NULLABLE"
                 ):
        self.name = name
        self.datatype = datatype
        self.description = description
        self.restricted_to = restricted_to
        self.mode = mode
        # whether it's a task for the LLM to complete.
        self.llm_task = False
        NodeProperty._instances.append(self)
    
    @classmethod
    def get_instances(cls):
        return cls._instances

# Define NodeProperties instances
label = NodeProperty(
    name="label",
    datatype="str",
    description="The type of content contained in the node",
    restricted_to=[
        "Personal Note", "Textbook", "Textbook Chapter",
        "Academic Paper", "Other"
    ],
    llm_task=True
)
author = NodeProperty(
    name="author",
    datatype="List[str]",
    description="The author(s) of the content",
    llm_task=True
)
content_creation_date = NodeProperty(
    name="content_creation_date",
    datatype=datetime,
    description="When hte node file was from",
)
file_creation_date = NodeProperty(
    name="file_creation_date",
    datatype=datetime,
    description="Date the node was created",
    mode="REQUIRED"
)
modification_date = NodeProperty(
    name="modification_date",
    datatype=datetime,
    description="Date the node was last modified",
    mode="REQUIRED"
)
filetype = NodeProperty(
    name="filetype",
    datatype="str",
    description="File type of the content",
    mode="REQUIRED"
)
location = NodeProperty(
    name="location",
    datatype="str",
    description="Location of the node (e.g., Notion, Local Files, OneDrive)",
    mode="REQUIRED"
)
path = NodeProperty(
    name="path",
    datatype="str",
    description="Path to the node file",
    mode="REQUIRED"
)
research_question = NodeProperty(
    name="research_question",
    datatype="str",
    description="Research question addressed by the node content",
    llm_task=True
)
main_argument = NodeProperty(
    name="main_argument",
    datatype="str",
    description="Main argument of the node content",
    llm_task=True
)
summary = NodeProperty(
    name="summary",
    datatype="str",
    description="Summary of the node content",
    llm_task=True
)
tags = NodeProperty(
    name="tags",
    datatype="List[str]",
    description="Tags associated with the node",
    llm_task=True
)
themes = NodeProperty(
    name="themes",
    datatype="List[str]",
    description="Themes related to the node",
    llm_task=True
)
keywords = NodeProperty(
    name="keywords",
    datatype="List[str]",
    description="Keywords related to the node",
    llm_task=True
)
quotes = NodeProperty(
    name="quotes",
    datatype="List[str]",
    description="Quotes from the node",
    llm_task=True
)
entities_persons = NodeProperty(
    name="entities_persons",
    datatype="List[str]",
    description="People mentioned in the node",
    llm_task=True
)
entities_places = NodeProperty(
    name="entities_places",
    datatype="List[str]",
    description="Places mentioned in the node",
    llm_task=True
)
entities_organizations = NodeProperty(
    name="entities_organizations",
    datatype="List[str]",
    description="Organizations mentioned in the node",
    llm_task=True
)
entities_references = NodeProperty(
    name="entities_references",
    datatype="List[str]",
    description="References mentioned in the node",
    llm_task=True
)
embedding = NodeProperty(
    name="embedding",
    datatype="List[float]",
    description="Embedding of the Node object",
)

NODE_PROPERTIES = NodeProperty.get_instances()

class Node:
    def __init__(self, **kwargs):
        # Unpack NODE_PROPERTIES directly into the Node instance
        for property in NODE_PROPERTIES:
            if property.name in kwargs:
                
                # validating data if restricted_to is not None
                if property.restricted_to is not None:
                    if kwargs[property.name] in property.restricted_to:
                        setattr(self, property.name, kwargs[property.name])
                    else:
                        setattr(self, property.name, None)
                
                else:  
                    setattr(self, property.name, kwargs[property.name])
            else:
                setattr(self, property.name, None)  # Set to None for properties not provided
    
    def __repr__(self):
        string = "Node(\n"
        for property in NODE_PROPERTIES:
            string += f"{property.name}={getattr(self, property.name)}\n"
        string += ")"
        return string
    



