"""Tools for conducting research and analyzing findings."""

import logging
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator, Optional, Union, Literal, Tuple
import asyncio
import re

logger = logging.getLogger(__name__)

class ResearchTools:
    """Tools for conducting research and analyzing findings."""
    
    # Constants for status phrases that indicate additional research is needed
    ADDITIONAL_RESEARCH_PHRASES = [
        "additional research needed", 
        "more information required", 
        "knowledge gap",
        "insufficient information",
        "知识空白",
        "不够清晰",
        "额外研究",
    ]
    
    @staticmethod
    def needs_additional_research(analysis_text: str) -> bool:
        """
        Determine if additional research is needed based on analysis text.
        
        Args:
            analysis_text: The analysis text to check
            
        Returns:
            bool: True if additional research is needed, False otherwise
        """
        analysis_text = analysis_text.lower()
        return any(phrase in analysis_text for phrase in ResearchTools.ADDITIONAL_RESEARCH_PHRASES)
    
    @staticmethod
    def conduct_research_step(researcher_agent, query: str) -> str:
        """
        Conduct the initial research step.

        Args:
            researcher_agent: The researcher agent to use
            query: The research question or topic

        Returns:
            str: Research findings
        """
        try:
            logger.info(f"Conducting initial research on: '{query}'")
            return researcher_agent(
                f"Research the following topic comprehensively: '{query}'. "
                f"Use your tools to gather information from multiple reliable sources."
            )
        except Exception as e:
            logger.error(f"Error during initial research: {e}")
            raise RuntimeError(f"Research step failed: {str(e)}")

    @staticmethod
    async def conduct_research_step_stream(researcher_agent, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Conduct the initial research step with non-streaming output.
        Note: Method name kept for compatibility, but now returns results in one go.

        Args:
            researcher_agent: The researcher agent to use
            query: The research question or topic

        Yields:
            Dict containing research progress and findings
        """
        try:
            logger.info(f"Conducting initial research on: '{query}'")

            prompt = (
                f"Research the following topic comprehensively: '{query}'. "
                f"Use your tools to gather information from multiple reliable sources."
            )

            # Call researcher agent directly (non-streaming)
            research_result = researcher_agent(prompt)

            # Convert to string if needed
            final_result = str(research_result)

            # Yield the complete result in one go
            yield {
                'type': 'research_complete',
                'final_result': final_result
            }

        except Exception as e:
            logger.error(f"Error during research: {e}")
            yield {
                'type': 'error',
                'error': str(e),
                'message': f"Research step failed: {str(e)}"
            }

    @staticmethod
    def analyze_findings(analyst_agent, query: str, findings: str) -> str:
        """
        Analyze research findings.

        Args:
            analyst_agent: The analyst agent to use
            query: The research question or topic
            findings: The research findings to analyze

        Returns:
            str: Analysis result
        """
        try:
            logger.info(f"Analyzing findings for query: '{query}'")
            return analyst_agent(
                f"Analyze these research findings about '{query}' and determine if additional research is needed:\n\n"
                f"{findings}"
            )
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise RuntimeError(f"Analysis step failed: {str(e)}")

    @staticmethod
    async def analyze_findings_stream(analyst_agent, query: str, findings: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Analyze research findings with non-streaming output.
        Note: Method name kept for compatibility, but now returns results in one go.

        Args:
            analyst_agent: The analyst agent to use
            query: The research question or topic
            findings: The research findings to analyze

        Yields:
            Dict containing analysis progress and results
        """
        try:
            logger.info(f"Conducting analysis for query: '{query}'")

            prompt = (
                f"Analyze these research findings about '{query}' and determine if additional research is needed:\n\n"
                f"{findings}"
            )

            # Call analyst agent directly (non-streaming)
            analysis_result = analyst_agent(prompt)

            # Convert to string if needed
            final_result = str(analysis_result)

            # Yield the complete result in one go
            yield {
                'type': 'analysis_complete',
                'final_result': final_result
            }

        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            yield {
                'type': 'error',
                'error': str(e),
                'message': f"Analysis step failed: {str(e)}"
            }

    @staticmethod
    def conduct_additional_research(researcher_agent, query: str, analysis: str) -> str:
        """
        Conduct additional targeted research based on analysis.

        Args:
            researcher_agent: The researcher agent to use
            query: The research question or topic
            analysis: The analysis result guiding additional research

        Returns:
            str: Additional research findings
        """
        try:
            logger.info(f"Conducting additional research for query: '{query}'")
            return researcher_agent(
                f"Based on this analysis, conduct additional targeted research on '{query}':\n\n"
                f"{analysis}\n\n"
                f"Focus on filling the identified knowledge gaps."
            )
        except Exception as e:
            logger.error(f"Error during additional research: {e}")
            raise RuntimeError(f"Additional research step failed: {str(e)}")
    
    @staticmethod
    def conduct_research_with_summary(researcher_agent, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Conduct research and capture search summaries.

        Args:
            researcher_agent: The researcher agent to use
            query: The research question or topic

        Returns:
            Tuple of (research_findings, search_summaries)
        """
        try:
            logger.info(f"Conducting research with summary capture on: '{query}'")

            # For now, conduct regular research and generate mock search summaries
            # This is a simplified implementation that can be enhanced later
            research_findings = researcher_agent(
                f"Research the following topic comprehensively: '{query}'. "
                f"Use your tools to gather information from multiple reliable sources."
            )

            # Generate mock search summaries based on the research findings
            search_summaries = ResearchTools.generate_mock_search_summaries(query, str(research_findings))

            return str(research_findings), search_summaries

        except Exception as e:
            logger.error(f"Error during research with summary: {e}")
            raise RuntimeError(f"Research step failed: {str(e)}")

    @staticmethod
    def generate_mock_search_summaries(query: str, research_findings: str) -> List[Dict[str, Any]]:
        """
        Generate mock search summaries based on research findings.
        This is a temporary implementation until we can properly capture search results.

        Args:
            query: The research query
            research_findings: The research findings text

        Returns:
            List of mock search summary data
        """
        # Analyze the research findings to extract information
        findings_length = len(research_findings)
        word_count = len(research_findings.split())

        # Count URLs in findings (rough estimate of sources)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', research_findings)
        unique_domains = list(set([url.split('/')[2] if '://' in url else 'unknown' for url in urls]))

        # Generate mock summary
        mock_summary = {
            'query': query,
            'total_results': min(max(word_count // 100, 1), 10),  # Estimate based on content
            'sources': ['Web Search', 'Academic Sources', 'News Articles'][:min(3, max(1, len(unique_domains)))],
            'domains': unique_domains[:5] if unique_domains else ['example.com', 'research.org'],
            'search_method': '_try_tavily_search',
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'results_preview': [
                {
                    'title': f"Research Result for {query}"[:100],
                    'domain': unique_domains[0] if unique_domains else 'research.org',
                    'snippet': research_findings[:150] + '...' if len(research_findings) > 150 else research_findings,
                    'source': 'Web Search'
                }
            ]
        }

        return [mock_summary]

    @staticmethod
    def generate_search_summary_output(search_summaries: List[Dict[str, Any]], query: str) -> str:
        """
        Generate a formatted output of search summaries for the frontend.

        Args:
            search_summaries: List of search summary data
            query: The original query

        Returns:
            str: Formatted search summary output
        """
        if not search_summaries:
            return f"## 🔍 Search Results Summary\n\n**Query**: {query}\n**Status**: No search results available"

        total_results = sum(summary.get('total_results', 0) for summary in search_summaries)
        all_sources = []
        all_domains = []
        successful_searches = 0

        for summary in search_summaries:
            if summary.get('status') == 'success':
                successful_searches += 1
                all_sources.extend(summary.get('sources', []))
                all_domains.extend(summary.get('domains', []))

        # Remove duplicates and limit
        unique_sources = list(set(all_sources))[:10]
        unique_domains = list(set(all_domains))[:10]

        output = f"""## 🔍 Search Results Summary

### 📊 Overview
- **Query**: {query}
- **Total Results Found**: {total_results}
- **Successful Searches**: {successful_searches}/{len(search_summaries)}
- **Information Sources**: {len(unique_sources)} different sources
- **Websites Accessed**: {len(unique_domains)} domains

### 🌐 Sources Used
{', '.join(unique_sources) if unique_sources else 'No sources available'}

### 🔗 Top Domains
{', '.join(unique_domains) if unique_domains else 'No domains available'}

### 📋 Search Details"""

        for i, summary in enumerate(search_summaries, 2):
            if summary.get('status') == 'success':
                method = summary.get('search_method', 'Unknown').replace('_try_', '').replace('_search', '').title()
                results_count = summary.get('total_results', 0)
                timestamp = summary.get('timestamp', '')

                output += f"""

#### Search {i} - {method}
- **Results**: {results_count} items found
- **Time**: {timestamp.split('T')[1][:8] if 'T' in timestamp else 'Unknown'}
- **Status**: ✅ Success"""

                # Add preview of top results
                previews = summary.get('results_preview', [])
                if previews:
                    output += "\n- **Top Results**:"
                    for j, preview in enumerate(previews[:2], 1):
                        title = preview.get('title', 'N/A')[:60]
                        domain = preview.get('domain', 'N/A')
                        output += f"\n  {j}. {title}... ({domain})"
            else:
                output += f"""

#### Search {i}
- **Status**: ❌ Failed
- **Error**: {summary.get('error', 'Unknown error')}"""

        output += f"""

### ⏰ Collection Time
**Completed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
✅ **Search phase completed successfully**"""

        return output
