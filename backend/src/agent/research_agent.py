"""Research Agent system using Strands Agents for comprehensive web research."""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator, Optional, Union, Literal, Tuple
from strands import Agent, tool
from dotenv import load_dotenv

# Import our tool classes
from .tools import ModelTools, LanguageTools, AgentCreationTools, ResearchTools, ReportTools
from .configuration import Configuration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ResearchAgentSystem:
    """Multi-agent research system using Strands Agents for comprehensive web research."""

    def __init__(
        self,
        config: Optional[Configuration] = None,
        language: str = "auto"
    ):
        """
        Initialize the research agent system.

        Args:
            config: Configuration object with model IDs for different stages
            language: The language to use for output (default: "auto" for auto-detection)
        """
        self.config = config or Configuration()

        # Initialize language tools
        self.language_tools = LanguageTools(language)

        # Create models using ModelTools based on configuration
        if self.config.model_type.lower() == "deepseek":
            # Use DeepSeek models for all agents
            self.researcher_model = ModelTools.create_deepseek_model(
                self.config.deepseek_model_id,
                self.config.deepseek_max_tokens,
                self.config.deepseek_temperature
            )
            self.analyst_model = ModelTools.create_deepseek_model(
                self.config.deepseek_model_id,
                self.config.deepseek_max_tokens,
                self.config.deepseek_temperature
            )
            self.writer_model = ModelTools.create_deepseek_model(
                self.config.deepseek_model_id,
                self.config.deepseek_max_tokens,
                self.config.deepseek_temperature
            )
        else:
            # Use Bedrock models (default)
            self.researcher_model = ModelTools.create_bedrock_model(self.config.query_generator_model)
            self.analyst_model = ModelTools.create_bedrock_model(self.config.reflection_model)
            self.writer_model = ModelTools.create_bedrock_model(self.config.answer_model)

        # Initialize agents with default language (will be recreated if language is auto-detected)
        self._current_language = "chinese" if self.language_tools.auto_detect_language else self.language_tools.language
        self.researcher_agent = AgentCreationTools.create_researcher_agent(self.researcher_model, self._current_language)
        self.analyst_agent = AgentCreationTools.create_analyst_agent(self.analyst_model, self._current_language)
        self.writer_agent = AgentCreationTools.create_writer_agent(self.writer_model, self._current_language)

        # Initialize orchestrator agent (will be created after language detection)
        self.orchestrator_agent = None

        if self.config.model_type.lower() == "deepseek":
            logger.info(f"Research agent system initialized with DeepSeek models: model_id={self.config.deepseek_model_id}, max_tokens={self.config.deepseek_max_tokens}, temperature={self.config.deepseek_temperature}")
        else:
            logger.info(f"Research agent system initialized with Bedrock models: researcher={self.config.query_generator_model}, analyst={self.config.reflection_model}, writer={self.config.answer_model}")

    
    
    async def research_stream(self, query: str, max_research_loops: Optional[int] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Conduct comprehensive research with streaming updates.

        Args:
            query: The research question or topic
            max_research_loops: Maximum number of research iterations (defaults to config value)

        Yields:
            Dictionary containing streaming updates
        """
        # Use config value if not specified
        if max_research_loops is None:
            max_research_loops = self.config.max_research_loops
        try:
            # Language Detection (if auto-detection is enabled)
            detected_language = self.language_tools.detect_and_set_language(query)
            logger.info(f"Using language: {detected_language}")

            # Enhanced initial status with comprehensive initialization info
            if self.config.model_type.lower() == "deepseek":
                models_info = {
                    'researcher': f"DeepSeek ({self.config.deepseek_model_id})",
                    'analyst': f"DeepSeek ({self.config.deepseek_model_id})",
                    'writer': f"DeepSeek ({self.config.deepseek_model_id})"
                }
            else:
                models_info = {
                    'researcher': self.config.query_generator_model.split(':')[0].split('.')[-1],
                    'analyst': self.config.reflection_model.split(':')[0].split('.')[-1],
                    'writer': self.config.answer_model.split(':')[0].split('.')[-1]
                }
            
            initialization_info = self.language_tools.generate_initialization_info(
                query, detected_language, max_research_loops, models_info
            )

            yield {
                'type': 'status',
                'message': f'🚀 Starting research for query: "{query[:50]}..."',
                'progress': 5,
                'step': 'initialization',
                'stage': 'initialization',
                'data': {
                    'stage_output': initialization_info,
                    'query': query,
                    'detected_language': detected_language,
                    'language_display': self.language_tools.get_current_language(),
                    'max_loops': max_research_loops,
                    'timestamp': datetime.now().isoformat()
                }
            }

            await asyncio.sleep(0.2)  # Small delay for UI responsiveness

            # System preparation status

            await asyncio.sleep(0.3)  # Small delay for UI responsiveness

            # Step 1: Initial Research with Streaming
            yield {
                'type': 'status',
                'message': '📚 Collecting initial information...',
                'progress': 15,
                'step': 'initial_research',
                'stage': 'research',
                'data': {
                    'stage_output': f"## Information Collection\n\n**Research Topic**: {query}\n**Search Strategy**: Multi-source information collection\n**Expected Sources**: Academic materials, news reports, official documents\n\nExecuting search..."
                }
            }

            # Conduct non-streaming research
            research_findings = ""
            search_summaries = []

            async for research_event in ResearchTools.conduct_research_step_stream(self.researcher_agent, query):
                if research_event['type'] == 'research_complete':
                    research_findings = research_event['final_result']
                    # Generate mock search summaries for compatibility
                    search_summaries = ResearchTools.generate_mock_search_summaries(query, research_findings)

                    # Show completion progress
                    yield {
                        'type': 'research_progress',
                        'message': '� Research completed',
                        'progress': 30,
                        'step': 'research_complete',
                        'stage': 'research',
                        'data': {
                            'stage_output': f"## Information Collection Completed\n\n**Research Topic**: {query}\n**Status**: Successfully collected comprehensive information\n\n**Research Summary**:\n{research_findings[:300]}..."
                        }
                    }
                    break
                elif research_event['type'] == 'error':
                    yield {
                        'type': 'error',
                        'message': f'Research error: {research_event["message"]}',
                        'error': research_event['error'],
                        'step': 'research_error',
                        'stage': 'research'
                    }
                    return

            # Generate search results summary for frontend
            search_summary_output = ResearchTools.generate_search_summary_output(search_summaries, query)

            yield {
                'type': 'progress',
                'message': '✅ Initial research completed',
                'progress': 35,
                'step': 'initial_research_complete',
                'stage': 'research',
                'data': {
                    'findings_preview': str(research_findings)[:200] + '...',
                    'search_summaries': search_summaries,
                    'stage_output': search_summary_output
                }
            }

            await asyncio.sleep(0.1)

            # Step 2: Analysis and Gap Identification with Streaming
            yield {
                'type': 'status',
                'message': '🔬 Analyzing research results and identifying knowledge gaps...',
                'progress': 45,
                'step': 'analysis',
                'stage': 'analysis',
                'data': {
                    'stage_output': f"## Analysis in Progress\n\n**Analysis Target**: Research findings for '{query}'\n**Analysis Method**: Comprehensive information evaluation\n**Objective**: Identify key knowledge points and potential gaps\n\nProcessing collected information..."
                }
            }

            # Conduct non-streaming analysis
            analysis_result = ""
            print(f"🔍 research_findings: {research_findings}")
            async for analysis_event in ResearchTools.analyze_findings_stream(self.analyst_agent, query, research_findings):
                if analysis_event['type'] == 'analysis_complete':
                    analysis_result = analysis_event['final_result']

                    # Show completion progress
                    yield {
                        'type': 'analysis_progress',
                        'message': '🔬 Analysis completed',
                        'progress': 52,
                        'step': 'analysis_complete',
                        'stage': 'analysis',
                        'data': {
                            'stage_output': f"## Analysis Completed\n\n**Analysis Target**: Research findings for '{query}'\n**Status**: Successfully analyzed research findings\n\n**Analysis Summary**:\n{analysis_result[:300]}..."
                        }
                    }
                    break
                elif analysis_event['type'] == 'error':
                    yield {
                        'type': 'error',
                        'message': f'Analysis error: {analysis_event["message"]}',
                        'error': analysis_event['error'],
                        'step': 'analysis_error',
                        'stage': 'analysis'
                    }
                    return

            yield {
                'type': 'progress',
                'message': '✅ Analysis completed',
                'progress': 55,
                'step': 'analysis_complete',
                'stage': 'analysis',
                'data': {
                    'analysis_preview': str(analysis_result)[:200] + '...',
                    'stage_output': f"## Analysis Results\n\n{str(analysis_result)[:600]}...\n\n**Analysis Method**: Comprehensive information evaluation\n**Key Findings**: Identified main knowledge points and potential gaps\n**Analysis Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }

            await asyncio.sleep(0.1)

            # Step 3: Additional Research (if needed)
            research_loop_count = 1
            print(f"🔍 analysis_result: {analysis_result}")
            while research_loop_count < max_research_loops:
                if ResearchTools.needs_additional_research(str(analysis_result)):
                    yield {
                        'type': 'status',
                        'message': f'🔄 Conducting round {research_loop_count} additional research...',
                        'progress': 60 + (research_loop_count * 10),
                        'step': f'additional_research_{research_loop_count}',
                        'stage': 'research',
                        'data': {
                            'stage_output': f"## Round {research_loop_count} Additional Research\n\n**Research Objective**: Fill knowledge gaps\n**Based on Analysis**: {str(analysis_result)[:200]}...\n\nExecuting deep search..."
                        }
                    }

                    # Conduct additional research (non-streaming for now to maintain compatibility)
                    additional_research = ResearchTools.conduct_additional_research(
                        self.researcher_agent, query, analysis_result
                    )

                    # Re-analyze with new information (non-streaming for now)
                    combined_findings = f"{research_findings}\n\n--- Additional Research ---\n\n{additional_research}"
                    analysis_result = ResearchTools.analyze_findings(
                        self.analyst_agent, query, combined_findings
                    )
                    research_findings = combined_findings
                    research_loop_count += 1

                    yield {
                        'type': 'progress',
                        'message': f'✅ Round {research_loop_count-1} additional research completed',
                        'progress': 65 + ((research_loop_count-1) * 10),
                        'step': f'additional_research_{research_loop_count-1}_complete',
                        'stage': 'research',
                        'data': {
                            'stage_output': f"## Round {research_loop_count-1} Additional Research Results\n\n{str(additional_research)[:500]}...\n\n**Research Depth**: Deep analysis\n**New Information**: Supplementary materials obtained\n**Completion Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    }

                    await asyncio.sleep(0.1)
                else:
                    break

            # Step 4: Final Report Generation with Streaming
            yield {
                'type': 'status',
                'message': '📝 Generating final report...',
                'progress': 85,
                'step': 'final_report',
                'stage': 'report',
                'data': {
                    'stage_output': f"## Final Report Generation\n\n**Report Topic**: {query}\n**Based on**: Comprehensive research and analysis\n**Format**: Structured markdown report\n\nGenerating comprehensive report..."
                }
            }

            # Start streaming report generation
            yield {
                'type': 'report_start',
                'message': 'Starting report content generation...',
                'progress': 87,
                'step': 'report_streaming_start',
                'stage': 'report'
            }

            final_report_chunks = []
            async for chunk in ReportTools.generate_final_report_stream(
                self.writer_agent, query, str(analysis_result), str(research_findings)
            ):
                final_report_chunks.append(chunk)
                yield {
                    'type': 'report_chunk',
                    'message': 'Generating report...',
                    'progress': min(87 + len(final_report_chunks) * 0.5, 95),
                    'step': 'report_streaming',
                    'stage': 'report',
                    'data': {
                        'chunk': chunk
                    }
                }
                await asyncio.sleep(0.01)  # Small delay for smooth streaming

            final_report = ''.join(final_report_chunks)

            yield {
                'type': 'progress',
                'message': '✅ Final report generation completed',
                'progress': 95,
                'step': 'final_report_complete',
                'stage': 'report'
            }

            await asyncio.sleep(0.1)

            # Final result
            yield {
                'type': 'complete',
                'message': '🎉 Research completed!',
                'progress': 100,
                'step': 'complete',
                'stage': 'complete',
                'data': {
                    'query': query,
                    'final_report': final_report,
                    'research_findings': str(research_findings),
                    'analysis': str(analysis_result),
                    'research_loops': research_loop_count,
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            yield {
                'type': 'error',
                'message': f'Error occurred during research: {str(e)}',
                'error': str(e),
                'step': 'error',
                'stage': 'error'
            }
