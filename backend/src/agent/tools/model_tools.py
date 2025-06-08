"""Tools for creating and managing Bedrock models."""

import logging
from strands.models import BedrockModel

logger = logging.getLogger(__name__)

class ModelTools:
    """Tools for creating and managing Bedrock models."""
    
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
