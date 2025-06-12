import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="us.anthropic.claude-3-haiku-20240307-v1:0",
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    reflection_model: str = Field(
        default="us.anthropic.claude-3-haiku-20240307-v1:0",
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    answer_model: str = Field(
        default="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    # Model type configuration
    model_type: str = Field(
        default="bedrock",
        metadata={
            "description": "The type of model provider to use ('bedrock' or 'deepseek')."
        },
    )

    # DeepSeek specific configuration
    deepseek_model_id: str = Field(
        default="deepseek-ai/DeepSeek-V3",
        metadata={
            "description": "The DeepSeek model ID to use when model_type is 'deepseek'."
        },
    )

    deepseek_max_tokens: int = Field(
        default=1000,
        metadata={
            "description": "Maximum tokens for DeepSeek model responses."
        },
    )

    deepseek_temperature: float = Field(
        default=0.7,
        metadata={
            "description": "Temperature for DeepSeek model response generation."
        },
    )

    # AWS credential configuration
    aws_use_default_credentials: bool = Field(
        default=False,
        metadata={
            "description": "Whether to use AWS default credential chain when env vars are not set."
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
