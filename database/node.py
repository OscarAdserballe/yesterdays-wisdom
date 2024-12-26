from datetime import datetime
import numpy as np

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class FileNode(BaseModel):
    """Properties extracted directly from the file system and file content"""
    primary_id: str = Field(description="Hash based on first and last 1024 characters of file uniquely identifying node.\
    Ontology of node is thus its content rather than anything reliant on metadata. Note issue with not registering changes in the middle")
    content: str = Field(description="The underlying content of the node")
    file_size: float = Field(description="Size of the node file in KB")
    file_creation_time: datetime = Field(description="Date the node was created")
    file_modification_time: datetime = Field(description="Date the node was last modified")
    filetype: str = Field(description="File type of the content")
    location: str = Field(description="Location of the node (e.g., Notion, Local Files, OneDrive)")
    path: str = Field(description="Path to the node file")
 
class LLMNode(BaseModel):
    """Properties derived from LLM analysis"""
    label: str = Field(description="The type of content contained in the node")
    author: List[str] = Field(description="The author(s) of the content")
    research_question: str = Field(description="Research question addressed by the node content")
    main_argument: str = Field(description="Main argument of the node content")
    summary: str = Field(description="Summary of the node content")
    tags: List[str] = Field(description="Tags associated with the node")
    themes: List[str] = Field(description="Themes related to the node's content")
    keywords: List[str] = Field(description="Keywords related to the node's content")
    quotes: List[str] = Field(description="Notable quotes from the node. List only a couple based on the length of the text. For example, a short text should only have 2-3 while longer papers should be upwards of 10")
    content_creation_date: datetime = Field(description="When the node file was from")
    entities_persons: List[str] = Field(description="People mentioned in the node")
    entities_places: List[str] = Field(description="Places mentioned in the node")
    entities_organizations: List[str] = Field(description="Organizations mentioned in the node")
    entities_references: List[str] = Field(description="References mentioned in the node")

class EmbeddingNode(BaseModel):
    """Node's content in embedding space"""
    content_embedding: list[float] = Field(description="Content of node in embedding space")

class Node(BaseModel):
    """Combined node with both file and LLM properties"""
    file: FileNode
    llm: LLMNode 
    embedding: EmbeddingNode 


