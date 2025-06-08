"""Web search tools for Strands Agent."""

import os
import requests
from typing import List, Dict, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from strands import tool


@tool
def get_page_content(url: str, max_chars: int = 6000) -> str:
    """
    Fetch and extract text content from a web page.
    
    Args:
        url: The URL to fetch content from
        max_chars: Maximum number of characters to return (default: 6000)
        
    Returns:
        Extracted text content from the web page
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:max_chars] if len(text) > max_chars else text
        
    except Exception as e:
        return f"Error fetching page content from {url}: {str(e)}"


@tool
def generate_search_queries(research_topic: str, num_queries: int = 3) -> str:
    """
    Generate optimized search queries for web research based on a research topic.
    
    Args:
        research_topic: The main topic or question to research
        num_queries: Number of search queries to generate (default: 3)
        
    Returns:
        List of optimized search queries formatted as a string
    """
    # This is a simple implementation - in practice, you might want to use
    # an LLM to generate more sophisticated queries
    base_queries = [
        research_topic,
        f"{research_topic} latest news",
        f"{research_topic} research studies",
        f"{research_topic} expert analysis",
        f"{research_topic} facts statistics"
    ]
    
    # Select the most relevant queries
    selected_queries = base_queries[:num_queries]
    
    formatted = f"Generated search queries for '{research_topic}':\n\n"
    for i, query in enumerate(selected_queries, 1):
        formatted += f"{i}. {query}\n"
    
    return formatted
