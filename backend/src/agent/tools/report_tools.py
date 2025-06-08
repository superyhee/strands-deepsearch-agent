"""Tools for generating research reports."""

import logging
from typing import AsyncGenerator, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class ReportTools:
    """Tools for generating research reports."""
    
    @staticmethod
    def generate_final_report(writer_agent, query: str, analysis: str, findings: str) -> str:
        """
        Generate the final research report.

        Args:
            writer_agent: The writer agent to use
            query: The research question or topic
            analysis: The analysis of research findings
            findings: The complete research findings

        Returns:
            str: Final report
        """
        try:
            logger.info(f"Generating final report for query: '{query}'")
            return writer_agent(
                f"Create a comprehensive research report on '{query}' based on this analysis:\n\n"
                f"{analysis}\n\n"
                f"Research findings:\n{findings}"
            )
        except Exception as e:
            logger.error(f"Error generating final report: {e}")
            raise RuntimeError(f"Report generation failed: {str(e)}")

    @staticmethod
    async def generate_final_report_stream(writer_agent, query: str, analysis: str, findings: str) -> AsyncGenerator[str, None]:
        """
        Generate the final research report with streaming output using Strands Agent.

        Args:
            writer_agent: The writer agent to use
            query: The research question or topic
            analysis: The analysis of research findings
            findings: The complete research findings

        Yields:
            str: Chunks of the final report as they are generated
        """
        try:
            logger.info(f"Generating streaming final report for query: '{query}'")

            # Create the prompt for the writer
            prompt = (
                f"Create a comprehensive research report on '{query}' based on this analysis:\n\n"
                f"{analysis}\n\n"
                f"Research findings:\n{findings}"
            )

            # Use Strands Agent's stream_async method for native streaming
            async for event in writer_agent.stream_async(prompt):
                # Handle different event types from Strands Agent
                if "data" in event:
                    # Text generation events - yield the text chunks
                    yield event["data"]
                elif "complete" in event and event["complete"]:
                    # Final chunk indicator
                    logger.info("Final report generation completed")
                    break
                elif "error" in event:
                    # Handle any errors from the agent
                    logger.error(f"Error in writer agent: {event['error']}")
                    yield f"抱歉，生成报告时出现错误: {event['error']}"
                    break

        except Exception as e:
            logger.error(f"Error generating streaming final report: {e}")
            yield f"抱歉，生成报告时出现错误: {str(e)}"
