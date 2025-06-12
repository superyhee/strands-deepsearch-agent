"""Main entry point for the Strands Agent research application."""

import os
import uvicorn
from dotenv import load_dotenv
from .utils.aws_credentials import print_aws_credential_status

# Load environment variables
load_dotenv()

def main():
    """Run the FastAPI application."""
    # Check AWS credentials configuration
    use_default_credentials = os.getenv("AWS_USE_DEFAULT_CREDENTIALS", "false").lower() == "true"

    # Validate AWS credentials
    if not print_aws_credential_status(use_default_credentials):
        return
    
    print("🚀 Starting Strands Agent Research API...")
    print(f"📍 AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    
    # Optional search API info
    if os.getenv('GOOGLE_SEARCH_API_KEY'):
        print("🔍 Google Search API configured")
    else:
        print("🔍 Using DuckDuckGo search fallback")
    
    # Run the FastAPI app
    uvicorn.run(
        "agent.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
