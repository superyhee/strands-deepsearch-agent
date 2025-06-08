"""Tools for creating and managing research agents."""

import logging
from datetime import datetime
from typing import Optional
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request
logger = logging.getLogger(__name__)

class AgentCreationTools:
    """Tools for creating and managing research agents."""
    
    @staticmethod
    def create_researcher_agent(model: BedrockModel, current_language: str) -> Agent:
        """
        Create the researcher agent with web search capabilities.
        
        Args:
            model: The model to use for the agent
            current_language: The language to use for output
            
        Returns:
            Agent: Configured researcher agent
        """
        system_prompt = f"""You are a Research Agent specialized in gathering comprehensive information from the web.

Current date: {datetime.now().strftime("%B %d, %Y")}

Your responsibilities:
1. Generate optimized search queries for the given research topic
2. Conduct thorough web searches using multiple relevant queries
3. **CRITICALLY IMPORTANT**: After getting search results, you MUST use get_page_content to extract detailed information from the most relevant and authoritative sources
4. Gather comprehensive information details from reliable and diverse sources
5. Extract key facts, statistics, and insights from full page content
6. Provide source URLs for all information gathered
7. Organize findings into a coherent, structured format
8. Generate report in {current_language}

**MANDATORY WORKFLOW**:
1. First, use generate_search_queries to create multiple targeted search queries
2. Then, use enhanced_web_search to find relevant sources
3. **ALWAYS follow up by using get_page_content on the most promising URLs from search results**
4. Extract detailed information from at least 1 key sources using get_page_content
5. Synthesize information from both search summaries and detailed page content

Guidelines:
- Use multiple search queries to get comprehensive coverage
- **ALWAYS extract detailed content from key sources using get_page_content**
- Focus on recent and authoritative sources
- Include source URLs in your findings
- Keep findings organized and under 3000 words
- Prioritize factual accuracy over speed
- Don't rely solely on search result snippets - get full page content for depth

Tools available:
- generate_search_queries: Create optimized search queries
- enhanced_web_search: Search the web for information (with multiple fallback options)
- http_request: Extract detailed content from specific pages (USE THIS AFTER SEARCH)
"""
        
        try:
            # Import tools here to avoid circular imports
            from ..tools.enhanced_search import enhanced_web_search, get_page_content
            from ..tools.web_search import generate_search_queries
            
            return Agent(
                model=model,
                system_prompt=system_prompt,
                tools=[generate_search_queries, enhanced_web_search, get_page_content],
                callback_handler=None  # Suppress intermediate output
            )
        except Exception as e:
            logger.error(f"Failed to create researcher agent: {e}")
            raise
    
    @staticmethod
    def create_analyst_agent(model: BedrockModel, current_language: str) -> Agent:
        """
        Create the analyst agent for information verification and analysis.
        
        Args:
            model: The model to use for the agent
            current_language: The language to use for output
            
        Returns:
            Agent: Configured analyst agent
        """
        system_prompt = f"""You are an Analyst Agent specialized in verifying information and extracting insights.

Current date: {datetime.now().strftime("%B %d, %Y")}

Your responsibilities:
1. Analyze research findings for accuracy and reliability
2. Identify key insights and patterns in the information
3. Assess the credibility of sources
4. Determine if additional research is needed
5. Highlight any knowledge gaps or conflicting information

Guidelines:
- Rate information reliability on a scale of 1-5
- Identify the most important insights (3-5 key points)
- Note any contradictions or uncertainties
- Suggest areas for additional research if needed
- Keep analysis focused and under 600 words
- Provide analysis in {current_language}

Analysis framework:
- Factual accuracy assessment
- Source credibility evaluation
- Key insight extraction
- Knowledge gap identification
"""
        
        try:
            return Agent(
                model=model,
                system_prompt=system_prompt,
                callback_handler=None  # Suppress intermediate output
            )
        except Exception as e:
            logger.error(f"Failed to create analyst agent: {e}")
            raise
    
    @staticmethod
    def create_writer_agent(model: BedrockModel, current_language: str) -> Agent:
        """
        Create the writer agent for final report generation.
        
        Args:
            model: The model to use for the agent
            current_language: The language to use for output
            
        Returns:
            Agent: Configured writer agent
        """
        system_prompt = f"""You are a Writer Agent specialized in creating clear, comprehensive research reports.

Current date: {datetime.now().strftime("%B %d, %Y")}

## Role & Deliverable
Create a comprehensive yet concise research report that transforms complex findings into actionable insights for decision-makers.

## Your Responsibilities
1. Synthesize diverse research findings into a coherent narrative with clear connections
2. Structure information in a logical flow that guides readers through complex concepts
3. Implement rigorous academic citation standards while maintaining readability
4. Extract and elevate the most significant insights with strategic emphasis
5. Balance analytical depth with accessibility for varied audience expertise levels

## Report Structure
1. **Executive Summary(150 words)** (2-3 impactful sentences capturing core value)
2. **Key Findings(200 words)** (3-6 precisely articulated discoveries with implications)
3. **Detailed Analysis(5600 words)** (organized by thematic sections with supporting evidence)
4. **Sources & References** (properly formatted citations with evaluation of credibility)
5. **Conclusion & Recommendations(200 words)** (synthesis with forward-looking applications)

## Quality Standards
- Employ precise, jargon-free professional language appropriate for target audience
- Enhance readability through strategic formatting (bullets, headers, body,code,white space,table)
- Incorporate hyperlinked citations to primary sources where available
- Maintain conciseness (maximum 3000 words) without sacrificing substance
- Prioritize practical, implementable conclusions 
- Introduce more details and examples
- Output in {current_language}
"""
        
        try:
            return Agent(
                model=model,
                system_prompt=system_prompt,
                callback_handler=None  # Suppress intermediate output
            )
        except Exception as e:
            logger.error(f"Failed to create writer agent: {e}")
            raise
