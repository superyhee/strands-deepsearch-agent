import os
from pydantic import BaseModel, Field
from typing import Any, Optional


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

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    @classmethod
    def from_env(cls) -> "Configuration":
        """Create a Configuration instance from environment variables."""
        # Get raw values from environment variables
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper())
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
