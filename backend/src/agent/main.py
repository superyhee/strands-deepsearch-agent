"""Main entry point for the Strands Agent research application."""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the FastAPI application."""
    # Check for required environment variables
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set up your AWS credentials in the .env file")
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
