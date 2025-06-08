from typing import Dict, List
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage


def get_research_topic(messages: List[AnyMessage]) -> str:
    """
    Get the research topic from the messages.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = messages[-1].content
    else:
        research_topic = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                research_topic += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                research_topic += f"Assistant: {message.content}\n"
    return research_topic


def format_sources_for_display(sources: List[Dict[str, str]]) -> str:
    """
    Format sources for display in the final answer.

    Args:
        sources: List of source dictionaries

    Returns:
        Formatted sources string
    """
    if not sources:
        return ""

    formatted_sources = "\n\n## Sources:\n"
    for i, source in enumerate(sources, 1):
        title = source.get('label', f'Source {i}')
        url = source.get('value', source.get('short_url', ''))
        snippet = source.get('snippet', '')

        formatted_sources += f"{i}. [{title}]({url})"
        if snippet:
            formatted_sources += f" - {snippet[:100]}..."
        formatted_sources += "\n"

    return formatted_sources



