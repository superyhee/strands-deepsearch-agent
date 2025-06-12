"""AWS credentials validation utilities."""

import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def validate_aws_credentials(use_default_credentials: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate AWS credentials based on configuration.
    
    Args:
        use_default_credentials: Whether to allow using AWS default credential chain
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # If environment variables are set, use them
    if aws_access_key and aws_secret_key:
        logger.info("Using AWS credentials from environment variables")
        return True, None
    
    # If environment variables are not set
    if not use_default_credentials:
        error_msg = (
            "Missing required environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY. "
            "Please either set these variables or enable AWS_USE_DEFAULT_CREDENTIALS=true"
        )
        return False, error_msg
    
    # Try to use default credential chain
    logger.info("AWS credentials not found in environment variables, trying default credential chain...")
    
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, PartialCredentialsError
        
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            error_msg = (
                "No AWS credentials found in credential chain. "
                "Please configure AWS credentials via environment variables, "
                "~/.aws/credentials file, or IAM roles"
            )
            return False, error_msg
        
        # Test the credentials by making a simple AWS call
        try:
            sts_client = boto3.client('sts')
            identity = sts_client.get_caller_identity()
            logger.info(f"Using AWS credentials from default chain - Account: {identity.get('Account', 'Unknown')}")
            return True, None
        except Exception as e:
            error_msg = f"AWS credentials found but validation failed: {e}"
            return False, error_msg
            
    except (NoCredentialsError, PartialCredentialsError) as e:
        error_msg = f"AWS credential error: {e}"
        return False, error_msg
    except ImportError:
        error_msg = "boto3 library not available for credential validation"
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to validate AWS credentials: {e}"
        return False, error_msg


def print_aws_credential_status(use_default_credentials: bool = False) -> bool:
    """
    Print AWS credential status and return whether credentials are valid.
    
    Args:
        use_default_credentials: Whether to allow using AWS default credential chain
        
    Returns:
        True if credentials are valid, False otherwise
    """
    is_valid, error_msg = validate_aws_credentials(use_default_credentials)
    
    if is_valid:
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        if aws_access_key:
            print("✅ Using AWS credentials from environment variables")
        else:
            print("✅ Using AWS credentials from default credential chain")
            try:
                import boto3
                sts_client = boto3.client('sts')
                identity = sts_client.get_caller_identity()
                print(f"📋 AWS Account: {identity.get('Account', 'Unknown')}")
                print(f"👤 AWS User/Role: {identity.get('Arn', 'Unknown')}")
            except Exception as e:
                print(f"⚠️  Warning: Could not get AWS identity info: {e}")
    else:
        print(f"❌ {error_msg}")
        if not use_default_credentials:
            print("💡 Tip: Set AWS_USE_DEFAULT_CREDENTIALS=true to use AWS credential chain")
        else:
            print("💡 Available credential sources:")
            print("  1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
            print("  2. AWS credentials file (~/.aws/credentials)")
            print("  3. IAM roles (if running on EC2)")
    
    return is_valid
