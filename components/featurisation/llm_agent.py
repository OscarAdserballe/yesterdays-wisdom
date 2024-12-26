from config.settings import LLM_MODEL, MAX_TOKEN_LIMIT
from pydantic_ai import Agent
from pydantic import BaseModel, Field

from database.node import LLMNode, FileNode

featurisation_prompt = """
You are will be provided a file node containing some content along with some metadata about some kind of file/paper/document.
Your task is to generate a list of features that can be used to represent the content and represent it more richly.
 
Please identify and extract the following information:
- Who are the authors of the content?
- What is the main research question being addressed?
- What is the main argument or thesis being presented?
- Provide a brief summary of the content
- What tags would you associate with this content?
- What are the main themes discussed?
- What are the key keywords or terms used?
- Extract important quotes from the text
- Who are the people mentioned in the content?
- What places are mentioned?
- What organizations are referenced?
- What external references or citations are included?

Don't worry if not all information is present, but fill in as many fields as possible.
"""

featurisation_agent = Agent(
    LLM_MODEL,
    result_type=LLMNode,
    system_prompt=featurisation_prompt
)

def content_made_llm_compatible(node: FileNode) -> str:
    """
    Cleaning content such that it can reliably be passed to LLM.
    Checks include:
    1. (Hacky!) Compressing if above token limit to first x tokens. 
    """
    # placeholder
    if len(node.content) < MAX_TOKEN_LIMIT:
        return node.content
    else:
        return node.content[:MAX_TOKEN_LIMIT]

async def file_node_to_llm_node(node: FileNode) -> LLMNode:
    result = featurisation_agent.run(
        f"Please featurise this node: {
            content_made_llm_compatible(node)
        }"
    )
    return LLMNode(
        **result.data
    ) 
