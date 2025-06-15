"""Tools for creating and managing research agents."""

import os
import logging
import json
from datetime import datetime
from typing import Optional, Union
from strands import Agent
from strands.models import BedrockModel
from strands.models.openai import OpenAIModel
from strands_tools import http_request
logger = logging.getLogger(__name__)


class DeepSeekAgentWrapper:
    """
    Wrapper for Strands Agent to handle DeepSeek's special tool calling format.
    """

    def __init__(self, agent: Agent):
        self.agent = agent

    def _parse_deepseek_tool_calls(self, content: str):
        """
        Parse DeepSeek's special tool calling format and convert to standard format.

        DeepSeek format: <｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>function_name
        ```json
        {"param": "value"}
        ```<｜tool▁call▁end｜><｜tool▁calls▁end｜>
        """
        if not content or '<｜tool▁calls▁begin｜>' not in content:
            return None

        try:
            # Extract function name
            if '<｜tool▁sep｜>' not in content:
                return None

            parts = content.split('<｜tool▁sep｜>')
            if len(parts) < 2:
                return None

            function_name = parts[1].split('\n')[0].strip()

            # Extract JSON parameters
            json_start = content.find('```json')
            json_end = content.find('```', json_start + 7)

            if json_start == -1 or json_end == -1:
                return None

            json_content = content[json_start + 7:json_end].strip()

            try:
                parameters = json.loads(json_content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON parameters: {json_content}")
                return None

            return {
                'function_name': function_name,
                'parameters': parameters
            }

        except Exception as e:
            logger.error(f"Failed to parse DeepSeek tool call format: {e}")
            return None

    def _execute_tool_call(self, tool_call_info):
        """Execute a tool call with the given parameters."""
        if not tool_call_info:
            print("🔧 No tool call info provided")
            return None

        # Debug agent attributes
        print(f"🔧 Agent type: {type(self.agent)}")
        print(f"🔧 Agent attributes: {[attr for attr in dir(self.agent) if not attr.startswith('_')]}")

        # Try different ways to access tools
        tools = None
        if hasattr(self.agent, 'tools'):
            tools = self.agent.tools
            print(f"🔧 Found tools via .tools: {len(tools) if tools else 0}")
        elif hasattr(self.agent, '_tools'):
            tools = self.agent._tools
            print(f"🔧 Found tools via ._tools: {len(tools) if tools else 0}")
        elif hasattr(self.agent, 'tool_specs'):
            tools = self.agent.tool_specs
            print(f"🔧 Found tools via .tool_specs: {len(tools) if tools else 0}")
        elif hasattr(self.agent, 'tool_registry'):
            # Try to get tools from tool_registry
            tool_registry = self.agent.tool_registry
            print(f"🔧 Tool registry type: {type(tool_registry)}")
            if hasattr(tool_registry, 'tools'):
                tools = tool_registry.tools
                print(f"🔧 Found tools via .tool_registry.tools: {len(tools) if tools else 0}")
            elif hasattr(tool_registry, '_tools'):
                tools = tool_registry._tools
                print(f"🔧 Found tools via .tool_registry._tools: {len(tools) if tools else 0}")
            elif hasattr(tool_registry, 'get_all_tools'):
                tools = tool_registry.get_all_tools()
                print(f"🔧 Found tools via .tool_registry.get_all_tools(): {len(tools) if tools else 0}")
            else:
                print(f"🔧 Tool registry attributes: {[attr for attr in dir(tool_registry) if not attr.startswith('_')]}")
                # Try to access registry directly
                if hasattr(tool_registry, 'registry'):
                    registry = tool_registry.registry
                    print(f"🔧 Registry type: {type(registry)}")
                    if isinstance(registry, dict):
                        print(f"🔧 Registry keys: {list(registry.keys())}")
                        if tool_call_info['function_name'] in registry:
                            tool = registry[tool_call_info['function_name']]
                            print(f"🔧 Found tool in registry: {tool_call_info['function_name']}, type: {type(tool)}")
                            try:
                                # Handle different tool types
                                if hasattr(tool, 'original_function'):
                                    # This is a FunctionTool, call the original function
                                    tool_result = tool.original_function(**tool_call_info['parameters'])
                                elif hasattr(tool, 'invoke'):
                                    # This has an invoke method
                                    tool_result = tool.invoke(**tool_call_info['parameters'])
                                elif hasattr(tool, 'func'):
                                    # This is a FunctionTool, call the underlying function
                                    tool_result = tool.func(**tool_call_info['parameters'])
                                elif hasattr(tool, '__call__'):
                                    # This is directly callable
                                    tool_result = tool(**tool_call_info['parameters'])
                                elif hasattr(tool, 'run'):
                                    # This has a run method
                                    tool_result = tool.run(**tool_call_info['parameters'])
                                else:
                                    print(f"🔧 Tool attributes: {[attr for attr in dir(tool) if not attr.startswith('_')]}")
                                    return None

                                print(f"🔧 Registry tool execution successful, result type: {type(tool_result)}")
                                return str(tool_result)
                            except Exception as e:
                                logger.error(f"Failed to execute registry tool {tool_call_info['function_name']}: {e}")
                                import traceback
                                traceback.print_exc()
                                return None

        if not tools:
            print("🔧 No tools found in agent")
            # Try to get tool by name directly
            if hasattr(self.agent, 'tool_registry') and hasattr(self.agent.tool_registry, 'get_tool'):
                try:
                    tool = self.agent.tool_registry.get_tool(tool_call_info['function_name'])
                    if tool:
                        print(f"🔧 Found tool directly by name: {tool_call_info['function_name']}")
                        try:
                            tool_result = tool(**tool_call_info['parameters'])
                            print(f"🔧 Direct tool execution successful, result type: {type(tool_result)}")
                            return str(tool_result)
                        except Exception as e:
                            logger.error(f"Failed to execute tool directly {tool_call_info['function_name']}: {e}")
                            import traceback
                            traceback.print_exc()
                            return None
                except Exception as e:
                    print(f"🔧 Failed to get tool directly: {e}")
            return None

        print(f"🔧 Agent has {len(tools)} tools available")

        # Find the matching tool
        matching_tool = None
        for i, tool in enumerate(tools):
            print(f"🔧 Tool {i}: {type(tool)}, name: {getattr(tool, 'name', 'no name')}, __name__: {getattr(tool, '__name__', 'no __name__')}")
            if hasattr(tool, 'name') and tool.name == tool_call_info['function_name']:
                matching_tool = tool
                print(f"🔧 Found matching tool by name: {tool.name}")
                break
            elif hasattr(tool, '__name__') and tool.__name__ == tool_call_info['function_name']:
                matching_tool = tool
                print(f"🔧 Found matching tool by __name__: {tool.__name__}")
                break

        if matching_tool:
            try:
                print(f"🔧 Executing DeepSeek tool call: {tool_call_info['function_name']} with params: {tool_call_info['parameters']}")

                # Execute the tool
                tool_result = matching_tool(**tool_call_info['parameters'])
                print(f"🔧 Tool execution successful, result type: {type(tool_result)}")
                return str(tool_result)

            except Exception as e:
                logger.error(f"Failed to execute tool {tool_call_info['function_name']}: {e}")
                import traceback
                traceback.print_exc()
                return None
        else:
            print(f"🔧 No matching tool found for: {tool_call_info['function_name']}")

        return None

    def __call__(self, prompt: str):
        """Call the agent and handle DeepSeek tool calling format."""
        try:
            # Call the original agent
            result = self.agent(prompt)

            # Extract content from result
            if hasattr(result, 'content'):
                content = result.content
            elif hasattr(result, 'text'):
                content = result.text
            else:
                content = str(result)

            print(f"🔍 Agent result content: {repr(content)}")

            # Check if the result contains DeepSeek tool calling format
            tool_call_info = self._parse_deepseek_tool_calls(content)

            if tool_call_info:
                print(f"🔧 Found DeepSeek tool call: {tool_call_info}")
                # Execute the tool call
                tool_result = self._execute_tool_call(tool_call_info)

                if tool_result:
                    print(f"🔧 Tool execution successful, result length: {len(tool_result)}")
                    # Create a new result with the tool output that mimics the original result structure
                    class ToolExecutionResult:
                        def __init__(self, content, original_result):
                            self.content = content
                            self.text = content  # For compatibility
                            # Copy other attributes from original result if they exist
                            if hasattr(original_result, '__dict__'):
                                for key, value in original_result.__dict__.items():
                                    if key not in ['content', 'text']:
                                        setattr(self, key, value)

                        def __str__(self):
                            return self.content

                    return ToolExecutionResult(tool_result, result)
                else:
                    print("🔧 Tool execution failed")
            else:
                print("🔍 No DeepSeek tool call format detected")

            # Return original result if no tool call or execution failed
            return result

        except Exception as e:
            logger.error(f"Error in DeepSeekAgentWrapper: {e}")
            import traceback
            traceback.print_exc()
            return self.agent(prompt)

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped agent."""
        return getattr(self.agent, name)

class AgentCreationTools:
    """Tools for creating and managing research agents."""

    @staticmethod
    def _should_enable_tools(model: Union[BedrockModel, OpenAIModel]) -> bool:
        """
        Check if tools should be enabled for the given model.

        Args:
            model: The model to check

        Returns:
            bool: True if tools should be enabled, False otherwise
        """
        # Check if this is a DeepSeek model (OpenAI model with SiliconFlow base URL)
        if isinstance(model, OpenAIModel):
            # Check if tools are explicitly disabled for DeepSeek
            deepseek_tools_enabled = os.getenv("DEEPSEEK_ENABLE_TOOLS", "true").lower() == "true"
            if not deepseek_tools_enabled:
                logger.info("Tools disabled for DeepSeek model due to DEEPSEEK_ENABLE_TOOLS=false")
                return False

        return True

    @staticmethod
    def _is_deepseek_model(model: Union[BedrockModel, OpenAIModel]) -> bool:
        """
        Check if the model is a DeepSeek model.

        Args:
            model: The model to check

        Returns:
            bool: True if this is a DeepSeek model, False otherwise
        """
        # Import here to avoid circular imports
        from .model_tools import DeepSeekModelWrapper

        # Check if this is our custom DeepSeekModelWrapper
        if isinstance(model, DeepSeekModelWrapper):
            logger.info("Detected DeepSeekModelWrapper")
            return True

        # Check if this is an OpenAI model with SiliconFlow base URL (indicating DeepSeek)
        if isinstance(model, OpenAIModel):
            logger.info(f"Checking if model is DeepSeek: {type(model)}")
            # Check various possible attributes for base URL
            base_url = None
            if hasattr(model, 'client_args') and model.client_args:
                base_url = model.client_args.get('base_url', '')
            elif hasattr(model, 'base_url'):
                base_url = model.base_url
            elif hasattr(model, '_client') and hasattr(model._client, 'base_url'):
                base_url = model._client.base_url

            if base_url:
                logger.info(f"Model base URL: {base_url}")
                is_deepseek = 'siliconflow' in base_url.lower()
                logger.info(f"Is DeepSeek model: {is_deepseek}")
                return is_deepseek
            else:
                logger.info("Could not find base URL in model")
        else:
            logger.info(f"Model is not OpenAI model: {type(model)}")
        return False
    
    @staticmethod
    def create_researcher_agent(model: Union[BedrockModel, OpenAIModel], current_language: str) -> Agent:
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
            # Check if tools should be enabled
            if AgentCreationTools._should_enable_tools(model):
                # Import tools here to avoid circular imports
                from ..tools.enhanced_search import enhanced_web_search, get_page_content
                from ..tools.web_search import generate_search_queries

                tools = [generate_search_queries, enhanced_web_search, get_page_content]
                logger.info("Creating researcher agent with tools enabled")
            else:
                tools = []
                logger.info("Creating researcher agent with tools disabled (DeepSeek compatibility mode)")
                # Update system prompt to indicate tools are not available
                system_prompt += "\n\nNote: External search tools are currently unavailable. Please provide responses based on your training data and clearly indicate when information might be outdated or when you recommend the user to search for current information manually."

            agent = Agent(
                model=model,
                system_prompt=system_prompt,
                tools=tools,
                callback_handler=None  # Suppress intermediate output
            )

            # Wrap with DeepSeek handler if this is a DeepSeek model
            if AgentCreationTools._is_deepseek_model(model):
                logger.info("Wrapping agent with DeepSeek tool calling handler")
                return DeepSeekAgentWrapper(agent)

            return agent
        except Exception as e:
            logger.error(f"Failed to create researcher agent: {e}")
            raise
    
    @staticmethod
    def create_analyst_agent(model: Union[BedrockModel, OpenAIModel], current_language: str) -> Agent:
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
    def create_writer_agent(model: Union[BedrockModel, OpenAIModel], current_language: str) -> Agent:
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

## IMPORTANT: Language Requirement
You MUST write the entire report in {current_language} language. This includes all sections, headings, content, and conclusions.

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
- **CRITICAL**: Write the entire report in {current_language} language
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
