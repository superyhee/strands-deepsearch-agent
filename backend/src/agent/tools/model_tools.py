"""Tools for creating and managing models."""

import os
import logging
import json
import re
from typing import Any, Dict, List, Optional, Union
from strands.models import BedrockModel
from strands.models.openai import OpenAIModel

logger = logging.getLogger(__name__)


class DeepSeekModelWrapper(OpenAIModel):
    """
    Custom wrapper for DeepSeek models via SiliconFlow API with enhanced tool calling support.

    This wrapper handles DeepSeek's special tool calling format and ensures proper execution.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("DeepSeek model wrapper initialized with enhanced tool calling support")

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
                import json
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

    def stream(self, request):
        """
        Override the stream method to fix tool message format and handle DeepSeek tool calling.
        """
        # Fix tool message content format for SiliconFlow API compatibility
        if hasattr(request, 'keys') and 'messages' in request:
            fixed_messages = []
            tool_messages_fixed = 0

            for msg in request['messages']:
                if isinstance(msg, dict) and msg.get('role') == 'tool':
                    fixed_msg = msg.copy()
                    content = msg.get('content', '')

                    # Convert list format to string format
                    if isinstance(content, list) and len(content) > 0:
                        if isinstance(content[0], dict) and 'text' in content[0]:
                            # Extract text from list format: [{'text': '...', 'type': 'text'}]
                            fixed_content = content[0]['text']
                            fixed_msg['content'] = fixed_content
                            tool_messages_fixed += 1

                    fixed_messages.append(fixed_msg)
                else:
                    fixed_messages.append(msg)

            # Update the request with fixed messages
            if tool_messages_fixed > 0:
                request = request.copy()
                request['messages'] = fixed_messages
                print(f"🔧 Fixed {tool_messages_fixed} tool message(s) for DeepSeek API compatibility")

        try:
            result = super().stream(request)
            return result
        except Exception as e:
            print(f"❌ DeepSeek API call failed: {e}")
            raise

    def converse(self, messages, tool_specs=None, system_prompt=None):
        """
        Override the converse method to handle DeepSeek tool calling format.
        """
        try:
            result = super().converse(messages, tool_specs, system_prompt)

            # Check if the result contains DeepSeek tool calling format
            if hasattr(result, 'content') and isinstance(result.content, str):
                tool_call_info = self._parse_deepseek_tool_calls(result.content)

                if tool_call_info and tool_specs:
                    # Find the matching tool
                    matching_tool = None
                    for tool_spec in tool_specs:
                        if hasattr(tool_spec, 'name') and tool_spec.name == tool_call_info['function_name']:
                            matching_tool = tool_spec
                            break
                        elif hasattr(tool_spec, '__name__') and tool_spec.__name__ == tool_call_info['function_name']:
                            matching_tool = tool_spec
                            break

                    if matching_tool:
                        try:
                            print(f"🔧 Executing DeepSeek tool call: {tool_call_info['function_name']} with params: {tool_call_info['parameters']}")

                            # Execute the tool
                            tool_result = matching_tool(**tool_call_info['parameters'])

                            # Create a new result with the tool output
                            class ToolExecutionResult:
                                def __init__(self, content):
                                    self.content = content

                                def __str__(self):
                                    return self.content

                            return ToolExecutionResult(str(tool_result))

                        except Exception as e:
                            logger.error(f"Failed to execute tool {tool_call_info['function_name']}: {e}")
                            # Return original result if tool execution fails
                            return result

            return result
        except Exception as e:
            print(f"❌ DeepSeek converse failed: {e}")
            raise


class ModelTools:
    """Tools for creating and managing models."""

    @staticmethod
    def create_bedrock_model(model_id: str) -> BedrockModel:
        """
        Create and configure the Bedrock model.

        Args:
            model_id: The Bedrock model ID to use

        Returns:
            BedrockModel: Configured model instance
        """
        # Create an actual model instance instead of just returning the ID string
        try:
            return BedrockModel(model_id=model_id)
        except Exception as e:
            logger.error(f"Failed to create Bedrock model {model_id}: {e}")
            raise

    @staticmethod
    def create_deepseek_model(model_id: str = "deepseek-ai/DeepSeek-V3", max_tokens: int = 2000, temperature: float = 0.3):
        """
        Create and configure the DeepSeek model via SiliconFlow API with optimized settings for tool calling.

        Args:
            model_id: The DeepSeek model ID to use (default: deepseek-ai/DeepSeek-V3)
            max_tokens: Maximum tokens for response (default: 2000, optimized for tool calling)
            temperature: Temperature for response generation (default: 0.3, lower for more consistent tool calling)

        Returns:
            DeepSeekModelWrapper: Configured DeepSeek model instance with tool calling optimization
        """
        try:
            # Get API key and base URL from environment
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.siliconflow.cn/v1")

            if not api_key:
                raise Exception("DEEPSEEK_API_KEY environment variable not set")

            # Set OpenAI environment variables for compatibility
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENAI_BASE_URL"] = base_url

            return DeepSeekModelWrapper(
                client_args={
                    "api_key": api_key,
                    "base_url": base_url
                },
                model_id=model_id,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(f"Failed to create DeepSeek model {model_id}: {e}")
            raise

    @staticmethod
    def create_model(model_id: str, model_type: str = "bedrock", **kwargs):
        """
        Create a model based on the model type.

        Args:
            model_id: The model ID to use
            model_type: The type of model ("bedrock" or "deepseek")
            **kwargs: Additional arguments for model creation

        Returns:
            Model instance
        """
        if model_type.lower() == "deepseek":
            return ModelTools.create_deepseek_model(model_id, **kwargs)
        else:
            return ModelTools.create_bedrock_model(model_id)
