#!/usr/bin/env python3
"""
Debug script to test DeepSeek tool calling with detailed logging.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_deepseek_with_simple_tool():
    """Test DeepSeek with a simple tool to see the debug output."""
    try:
        from agent.tools.model_tools import ModelTools
        from strands import Agent
        from strands import tool

        print("🔧 Testing DeepSeek with simple tool and detailed debugging...")

        # Create a simple test tool
        @tool
        def simple_test_tool(message: str) -> str:
            """A simple test tool that returns a message."""
            print(f"🔧 TOOL EXECUTED: simple_test_tool with message: {repr(message)}")
            return f"Tool received: {message}"

        # Create DeepSeek model with debugging
        model = ModelTools.create_deepseek_model()
        print("✅ DeepSeek model created with debugging")

        # Create agent with simple tool
        agent = Agent(
            model=model,
            system_prompt="You are a helpful assistant. When asked to use a tool, use the simple_test_tool.",
            tools=[simple_test_tool],
            callback_handler=None
        )
        print("✅ Agent created with simple tool")

        # Test tool call
        print("\n🧪 Testing tool call...")
        print("📤 Sending prompt that should trigger tool usage...")
        
        test_prompt = "Please use the simple_test_tool with the message 'hello world'."
        print(f"📤 Prompt: {test_prompt}")
        
        response = agent(test_prompt)
        print(f"📥 Final response: {response}")
        print("✅ Tool call test completed!")

        return True

    except Exception as e:
        print(f"❌ Tool call test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_deepseek_with_search_tool():
    """Test DeepSeek with actual search tools."""
    try:
        from agent.tools.model_tools import ModelTools
        from agent.tools.agent_creation_tools import AgentCreationTools

        print("\n🔧 Testing DeepSeek with search tools...")

        # Create DeepSeek model with higher max_tokens for complete responses
        model = ModelTools.create_deepseek_model(max_tokens=2000, temperature=0.3)
        print("✅ DeepSeek model created with higher token limit")

        # Create researcher agent with tools
        agent = AgentCreationTools.create_researcher_agent(model, "chinese")
        print("✅ Researcher agent created")

        # Test search with a simpler prompt
        print("\n🧪 Testing search tool call...")
        test_prompt = "请搜索2024年最新的科幻电影，并给我一个简短的总结。"
        print(f"📤 Prompt: {test_prompt}")

        response = agent(test_prompt)
        print(f"📥 Response type: {type(response)}")

        # Extract the actual text from AgentResult
        if hasattr(response, 'content'):
            response_text = response.content
        elif hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = str(response)

        print(f"📥 Final response length: {len(response_text)} characters")
        print(f"📥 Final response: {response_text}")
        print("✅ Search tool test completed!")

        return True

    except Exception as e:
        print(f"❌ Search tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 DeepSeek Tool Calling Debug")
    print("=" * 50)
    
    # Test with simple tool first
    simple_ok = test_deepseek_with_simple_tool()
    
    # Test with search tools if simple tool works
    if simple_ok:
        search_ok = test_deepseek_with_search_tool()
    else:
        search_ok = False
    
    print("\n" + "=" * 50)
    print("📊 Debug Results:")
    print(f"  Simple Tool Test: {'✅ PASS' if simple_ok else '❌ FAIL'}")
    print(f"  Search Tool Test: {'✅ PASS' if search_ok else '❌ FAIL'}")
