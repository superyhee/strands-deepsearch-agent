"""Enhanced web search tools with multiple fallback options."""

import os
import requests
import json
from typing import List, Dict, Any, Tuple
from urllib.parse import quote_plus
from strands import tool
from datetime import datetime

# Conditional import for tavily
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    TavilyClient = None

# Conditional import for googlesearch
try:
    from googlesearch import search
    GOOGLESEARCH_AVAILABLE = True
except ImportError:
    GOOGLESEARCH_AVAILABLE = False
    search = None


@tool
def enhanced_web_search(query: str, num_results: int = 10) -> str:
    """
    Enhanced web search with multiple fallback options.
    
    Args:
        query: The search query string
        num_results: Number of search results to return (default: 5, max: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    print(f"🔍 Searching for: {query}")
    
    # Try multiple search methods in order of preference
    search_methods = [
        _try_tavily_search,
        _try_serpapi_search,
        _try_google_search,
        _try_googlesearch_library,
        _try_duckduckgo_search,
        _try_wikipedia_search,
        _try_news_search
    ]
    
    for method in search_methods:
        try:
            results = method(query, num_results)
            if results:
                print(f"✅ Search successful using {method.__name__}")
                return results
        except Exception as e:
            print(f"❌ {method.__name__} failed: {e}")
            continue
    
    # If all methods fail, return a helpful message
    return f"""Search temporarily unavailable for query: '{query}'

I apologize, but I'm currently unable to access external search engines due to network connectivity issues. However, I can still provide information based on my training data.

For the topic '{query}', I can offer general information and insights. Please let me know if you'd like me to provide what I know about this subject, or if you'd prefer to try the search again later."""


def _try_tavily_search(query: str, num_results: int, search_depth: str = "advanced") -> List[Dict[str, Any]]:
    """Try Tavily Search API."""
    if not TAVILY_AVAILABLE:
        raise Exception("Tavily library not available")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise Exception("Tavily Search API key not configured")
    print(f"🔍 num_results: {num_results}")
    tavily_client = TavilyClient(api_key=api_key)
    
    # 调用Tavily搜索API
    response = tavily_client.search(
        query=query,
        search_depth=search_depth,  # 可选值: "basic" 或 "advanced"
        max_results=min(num_results, 10),
        include_domains=[],  # 可选: 指定要包含的域名
        exclude_domains=[],  # 可选: 指定要排除的域名
        include_answer=True,  # 是否包含AI生成的摘要答案
        include_raw_content= False,  # 是否包含原始内容
    )
    
    results = []
    
    # 处理搜索结果
    if response and "results" in response:
        for item in response["results"][:num_results]:
            results.append({
                'title': item.get('title', ''),
                'link': item.get('url', ''),
                'snippet': item.get('content', ''),
                'source': 'Tavily'
            })
  
    return results


def _try_serpapi_search(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Try SerpAPI Search."""
    api_key = os.getenv("SERPAPI_API_KEY")

    if not api_key:
        raise Exception("SerpAPI key not configured")

    params = {
        "api_key": api_key,
        "engine": "google",
        "q": query,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "num": min(num_results, 10)
    }

    url = "https://serpapi.com/search"
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    results = []

    # Process organic results
    organic_results = data.get('organic_results', [])
    for item in organic_results[:num_results]:
        results.append({
            'title': item.get('title', ''),
            'link': item.get('link', ''),
            'snippet': item.get('snippet', ''),
            'source': 'SerpAPI'
        })

    return results


def _try_google_search(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Try Google Custom Search API."""
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not api_key or not search_engine_id:
        raise Exception("Google Search API credentials not configured")
    
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'num': min(num_results, 10)
    }
    
    response = requests.get(base_url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    if 'items' in data:
        for item in data['items']:
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': item.get('displayLink', '')
            })
    
    return results


def _try_googlesearch_library(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Try googlesearch library (free Google search without API key)."""
    if not GOOGLESEARCH_AVAILABLE:
        raise Exception("googlesearch library not available")

    try:
        # Use the googlesearch library to perform search
        # The search function returns URLs, we need to get titles and snippets separately
        search_results = search(query, advanced=True, num_results=min(num_results, 10))

        results = []
        for result in search_results:
            # The advanced=True option returns SearchResult objects with url, title, description
            if hasattr(result, 'url') and hasattr(result, 'title'):
                results.append({
                    'title': result.title or 'No title available',
                    'link': result.url,
                    'snippet': getattr(result, 'description', '') or 'No description available',
                    'source': 'GoogleSearch Library'
                })
            else:
                # Fallback for simple URL results
                results.append({
                    'title': f"Search result for: {query}",
                    'link': str(result),
                    'snippet': 'No description available',
                    'source': 'GoogleSearch Library'
                })

            if len(results) >= num_results:
                break

        return results

    except Exception as e:
        raise Exception(f"GoogleSearch library error: {str(e)}")


def _try_duckduckgo_search(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Try DuckDuckGo search."""
    url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
    
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    # Add abstract if available
    if data.get('Abstract'):
        results.append({
            'title': data.get('AbstractSource', 'DuckDuckGo'),
            'link': data.get('AbstractURL', ''),
            'snippet': data.get('Abstract', ''),
            'source': data.get('AbstractSource', '')
        })
    
    # Add related topics
    for topic in data.get('RelatedTopics', [])[:num_results-1]:
        if isinstance(topic, dict) and 'Text' in topic:
            results.append({
                'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                'link': topic.get('FirstURL', ''),
                'snippet': topic.get('Text', ''),
                'source': topic.get('FirstURL', '').split('/')[2] if topic.get('FirstURL') else ''
            })
    
    return results[:num_results]


def _try_wikipedia_search(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Try Wikipedia search as fallback."""
    search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(query)
    
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [{
                'title': data.get('title', query),
                'link': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'snippet': data.get('extract', ''),
                'source': 'Wikipedia'
            }]
    except:
        pass
    
    # Try Wikipedia search API
    search_api = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': query,
        'srlimit': min(num_results, 5)
    }
    
    response = requests.get(search_api, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    for item in data.get('query', {}).get('search', []):
        results.append({
            'title': item.get('title', ''),
            'link': f"https://en.wikipedia.org/wiki/{quote_plus(item.get('title', ''))}",
            'snippet': item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', ''),
            'source': 'Wikipedia'
        })
    
    return results


def _try_news_search(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Try news search as another fallback."""
    # This is a placeholder for news API integration
    # You could integrate with NewsAPI, Bing News, etc.
    return []


def _format_search_results(results: List[Dict[str, Any]], query: str) -> str:
    """Format search results for the agent with enhanced DeepSeek API compatibility."""
    if not results:
        return f"No search results found for query: {query}"

    # Create detailed search summary
    sources = list(set([result.get('source', 'Unknown') for result in results if result.get('source')]))

    # Enhanced cleaning function for DeepSeek API compatibility
    def clean_text_for_deepseek(text: str) -> str:
        """Clean text to ensure compatibility with DeepSeek API."""
        if not text:
            return ""

        # Convert to string if not already
        text = str(text)

        # Remove null bytes and other problematic characters
        text = text.replace('\x00', '')

        # Remove or replace non-printable characters except common whitespace
        import re
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', ' ', text)

        # Replace problematic Unicode characters that might cause issues
        text = re.sub(r'[^\x20-\x7E\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]', ' ', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Ensure the string is not empty
        if not text.strip():
            return "N/A"

        return text.strip()

    # Clean query for safe display
    clean_query = clean_text_for_deepseek(query)

    formatted = f"""## Search Results Summary
**Query**: {clean_query}
**Results Count**: {len(results)}
**Sources**: {', '.join([clean_text_for_deepseek(s) for s in sources])}
**Search Time**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Detailed Results

"""

    for i, result in enumerate(results, 1):
        # Clean all text fields to ensure they are valid strings
        title = clean_text_for_deepseek(result.get('title', 'N/A'))
        url = str(result.get('link', 'N/A'))  # URLs should be ASCII-safe
        snippet = clean_text_for_deepseek(result.get('snippet', 'N/A'))
        source = clean_text_for_deepseek(result.get('source', 'N/A'))

        # Limit individual field lengths
        title = title[:200] if len(title) > 200 else title
        snippet = snippet[:500] if len(snippet) > 500 else snippet
        source = source[:100] if len(source) > 100 else source

        formatted += f"### Result {i}: {title}\n"
        formatted += f"**Source**: {source}\n"
        formatted += f"**URL**: {url}\n"
        formatted += f"**Summary**: {snippet}\n\n"
        formatted += "---\n\n"

    # Final cleanup of the entire formatted string
    formatted = clean_text_for_deepseek(formatted)

    # Limit total length to prevent API issues with DeepSeek
    max_total_length = 2500  # Conservative limit for DeepSeek API
    if len(formatted) > max_total_length:
        formatted = formatted[:max_total_length] + "\n\n[Search results truncated due to length limit]"

    # Ensure the result is a valid string
    if not formatted or not formatted.strip():
        return f"Search completed for query: {clean_query}, but no valid results could be formatted."

    return formatted


def enhanced_web_search_with_summary(query: str, num_results: int = 5) -> Tuple[str, Dict[str, Any]]:
    """
    Enhanced web search that returns both formatted results and summary data.

    Args:
        query: The search query string
        num_results: Number of search results to return (default: 5, max: 10)

    Returns:
        Tuple of (formatted_results, summary_data)
    """
    print(f"🔍 Searching for: {query}")

    # Try multiple search methods in order of preference
    search_methods = [
        _try_tavily_search,
        _try_serpapi_search,
        _try_google_search,
        _try_googlesearch_library,
        _try_duckduckgo_search,
        _try_wikipedia_search,
        _try_news_search
    ]

    results = []
    successful_method = None

    for method in search_methods:
        try:
            results = method(query, num_results)
            if results:
                successful_method = method.__name__
                print(f"✅ Search successful using {method.__name__}")
                break
        except Exception as e:
            print(f"❌ {method.__name__} failed: {e}")
            continue

    if not results:
        # If all methods fail, return empty results
        summary_data = {
            'query': query,
            'total_results': 0,
            'sources': [],
            'search_method': 'failed',
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'error': 'All search methods failed'
        }
        formatted_results = f"Search temporarily unavailable for query: '{query}'"
        return formatted_results, summary_data

    # Generate summary data
    sources = list(set([result.get('source', 'Unknown') for result in results if result.get('source')]))
    domains = list(set([result.get('link', '').split('/')[2] if result.get('link') and '://' in result.get('link', '') else 'Unknown' for result in results]))
    domains = [d for d in domains if d != 'Unknown']

    summary_data = {
        'query': query,
        'total_results': len(results),
        'sources': sources,
        'domains': domains[:5],  # Top 5 domains
        'search_method': successful_method,
        'timestamp': datetime.now().isoformat(),
        'status': 'success',
        'results_preview': [
            {
                'title': result.get('title', 'N/A')[:100],
                'domain': result.get('link', '').split('/')[2] if result.get('link') and '://' in result.get('link', '') else 'Unknown',
                'snippet': result.get('snippet', 'N/A')[:150],
                'source': result.get('source', 'Unknown')
            }
            for result in results[:3]  # Top 3 results preview
        ]
    }

    # Format results
    formatted_results = _format_search_results(results, query)

    return formatted_results, summary_data


@tool
def get_page_content(url: str, max_chars: int = 4000) -> str:
    """
    Fetch and extract text content from a web page and convert it to markdown.
    
    Args:
        url: The URL to fetch content from
        max_chars: Maximum number of characters to return (default: 2000)
        
    Returns:
        Extracted text content from the web page as markdown
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
       
        # Use BeautifulSoup for better HTML parsing and HTML to Markdown conversion
        try:
            from bs4 import BeautifulSoup
            from markdownify import markdownify as md
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'iframe']):
                element.decompose()
            
            print(f"✅ 成功从 {url} 获取内容")
            # Convert HTML to Markdown
            markdown_content = md(str(soup))

            # Clean up the markdown
            import re
            markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)  # Remove excess newlines
            markdown_content = markdown_content.strip()

            # Enhanced content cleaning for DeepSeek API compatibility
            def clean_content_for_deepseek(content: str) -> str:
                """Clean content to ensure compatibility with DeepSeek API."""
                if not content:
                    return ""

                # Remove null bytes and other problematic characters
                content = content.replace('\x00', '')

                # Remove or replace non-printable characters except common whitespace
                content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', ' ', content)

                # Replace problematic Unicode characters that might cause issues
                content = re.sub(r'[^\x20-\x7E\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]', ' ', content)

                # Normalize whitespace
                content = re.sub(r'\s+', ' ', content)

                return content.strip()

            markdown_content = clean_content_for_deepseek(markdown_content)
            title_text = clean_content_for_deepseek(soup.title.text if soup.title else "Web Page")

            result = f"""## Web Content: {title_text}
**Source**: {url}
**Retrieved**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{markdown_content[:max_chars] if len(markdown_content) > max_chars else markdown_content}
"""
            if len(markdown_content) > max_chars:
                result += "\n\n[Content truncated due to length limit]"

            # Final cleanup of the result
            result = clean_content_for_deepseek(result)

            # Ensure the result is not empty
            if not result or not result.strip():
                return f"Successfully retrieved content from {url}, but content could not be properly formatted."

            print(f"✅ Successfully retrieved content, length: {len(result)} characters")
            return result
            
        except ImportError:
            # Fallback if markdownify or BeautifulSoup is not available
            import re
            text = response.text
            text = re.sub(r'<[^>]+>', ' ', text)  # Remove HTML tags
            text = re.sub(r'\s+', ' ', text)      # Normalize whitespace
            text = text.strip()
            
            result = f"""## 网页内容
**来源**: {url}
**获取时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{text[:max_chars] if len(text) > max_chars else text}
"""
            if len(text) > max_chars:
                result += "\n\n[内容已截断，超出字符限制]"
                
            return result
        
    except Exception as e:
        return f"Error fetching page content from {url}: {str(e)}"


@tool
def serpapi_search(query: str, num_results: int = 5) -> str:
    """
    使用SerpAPI搜索引擎进行网络搜索。

    Args:
        query: 搜索查询字符串
        num_results: 返回的搜索结果数量（默认为5，最大为10）

    Returns:
        格式化的搜索结果，包含标题、URL和摘要
    """
    print(f"🔍 使用SerpAPI搜索: {query}")

    try:
        results = _try_serpapi_search(query, num_results)
        if results:
            return _format_search_results(results, query)
        else:
            return f"未找到与'{query}'相关的搜索结果"
    except Exception as e:
        return f"SerpAPI搜索失败: {str(e)}\n请检查SERPAPI_API_KEY环境变量是否已正确配置。"


@tool
def tavily_search(query: str, search_depth: str = "advanced", num_results: int = 5) -> str:
    """
    使用Tavily搜索引擎进行网络搜索。

    Args:
        query: 搜索查询字符串
        search_depth: 搜索深度，可选值为"basic"或"advanced"（默认为"advanced"）
        num_results: 返回的搜索结果数量（默认为5，最大为10）

    Returns:
        格式化的搜索结果，包含标题、URL和摘要
    """
    print(f"🔍 使用Tavily搜索: {query}")

    try:
        results = _try_tavily_search(query, num_results, search_depth)
        if results:
            return _format_search_results(results, query)
        else:
            return f"未找到与'{query}'相关的搜索结果"
    except Exception as e:
        return f"Tavily搜索失败: {str(e)}\n请检查TAVILY_API_KEY环境变量是否已正确配置。"


@tool
def googlesearch_library_search(query: str, num_results: int = 5) -> str:
    """
    使用googlesearch库进行免费的Google搜索（无需API密钥）。

    Args:
        query: 搜索查询字符串
        num_results: 返回的搜索结果数量（默认为5，最大为10）

    Returns:
        格式化的搜索结果，包含标题、URL和摘要
    """
    print(f"🔍 使用GoogleSearch库搜索: {query}")

    try:
        results = _try_googlesearch_library(query, num_results)
        if results:
            return _format_search_results(results, query)
        else:
            return f"未找到与'{query}'相关的搜索结果"
    except Exception as e:
        return f"GoogleSearch库搜索失败: {str(e)}\n请确保已安装googlesearch-python库: pip install googlesearch-python"
