#!/usr/bin/env python3
"""Test script to verify DeepSeek model configuration and basic functionality."""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_deepseek_model():
    """Test DeepSeek model creation and basic functionality."""
    try:
        from agent.tools.model_tools import ModelTools
        
        print("🔧 Testing DeepSeek model creation...")
        
        # Check environment variables
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        model_type = os.getenv("MODEL_TYPE")
        
        print(f"📋 Environment variables:")
        print(f"  DEEPSEEK_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
        print(f"  DEEPSEEK_BASE_URL: {base_url or 'Not set'}")
        print(f"  MODEL_TYPE: {model_type or 'Not set'}")
        
        if not api_key:
            print("❌ DEEPSEEK_API_KEY not set. Please configure it in .env file.")
            return False
        
        # Create DeepSeek model
        print("\n🚀 Creating DeepSeek model...")
        model = ModelTools.create_deepseek_model()
        print(f"✅ Model created successfully: {type(model)}")
        
        # Test basic model call
        print("\n🧪 Testing basic model call...")
        try:
            # Simple test message
            test_message = "Hello, please respond with 'Hello World' in English."
            print(f"📤 Sending test message: {test_message}")
            
            # Use the model directly
            response = model.invoke(test_message)
            print(f"📥 Response: {response}")
            print("✅ Basic model call successful!")
            
        except Exception as e:
            print(f"❌ Model call failed: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration loading."""
    try:
        from agent.configuration import Configuration
        
        print("\n🔧 Testing configuration loading...")
        
        # Create configuration from environment
        config = Configuration.from_runnable_config()
        
        print(f"📋 Configuration loaded:")
        print(f"  model_type: {config.model_type}")
        print(f"  deepseek_model_id: {config.deepseek_model_id}")
        print(f"  deepseek_max_tokens: {config.deepseek_max_tokens}")
        print(f"  deepseek_temperature: {config.deepseek_temperature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_creation():
    """Test agent creation with DeepSeek model."""
    try:
        from agent.tools.model_tools import ModelTools
        from agent.tools.agent_creation_tools import AgentCreationTools

        print("\n🔧 Testing agent creation...")

        # Create DeepSeek model
        model = ModelTools.create_deepseek_model()
        print("✅ Model created for agent")

        # Create a simple analyst agent (no tools required)
        agent = AgentCreationTools.create_analyst_agent(model, "english")
        print("✅ Agent created successfully")

        # Test simple agent call
        print("\n🧪 Testing agent call...")
        test_prompt = "Please analyze this simple statement: 'The sky is blue.' Provide a brief analysis in English."
        response = agent(test_prompt)
        print(f"📥 Agent response: {response}")
        print("✅ Agent call successful!")

        return True

    except Exception as e:
        print(f"❌ Agent creation/call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_researcher_agent_with_tools():
    """Test researcher agent with tools (this might fail due to tool issues)."""
    try:
        from agent.tools.model_tools import ModelTools
        from agent.tools.agent_creation_tools import AgentCreationTools

        print("\n🔧 Testing researcher agent with tools...")

        # Create DeepSeek model
        model = ModelTools.create_deepseek_model()
        print("✅ Model created for researcher agent")

        # Create researcher agent (has tools)
        agent = AgentCreationTools.create_researcher_agent(model, "english")
        print("✅ Researcher agent created successfully")

        # Test simple research call without actually using tools
        print("\n🧪 Testing researcher agent call...")
        test_prompt = "Please provide a brief overview of artificial intelligence. Do not use any tools, just provide your knowledge."
        response = agent(test_prompt)
        print(f"📥 Researcher agent response: {response}")
        print("✅ Researcher agent call successful!")

        return True

    except Exception as e:
        print(f"❌ Researcher agent creation/call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_researcher_agent_with_actual_tools():
    """Test researcher agent with actual tool usage (this will likely reproduce the error)."""
    try:
        from agent.tools.model_tools import ModelTools
        from agent.tools.agent_creation_tools import AgentCreationTools

        print("\n🔧 Testing researcher agent with ACTUAL tool usage...")

        # Create DeepSeek model
        model = ModelTools.create_deepseek_model()
        print("✅ Model created for researcher agent")

        # Create researcher agent (has tools)
        agent = AgentCreationTools.create_researcher_agent(model, "chinese")
        print("✅ Researcher agent created successfully")

        # Test research call that WILL use tools
        print("\n🧪 Testing researcher agent call with tool usage...")
        test_prompt = "搜索最新的科幻电影信息。请使用你的搜索工具来查找相关信息。"
        print(f"📤 Sending prompt: {test_prompt}")
        response = agent(test_prompt)
        print(f"📥 Researcher agent response: {response}")
        print("✅ Researcher agent with tools call successful!")

        return True

    except Exception as e:
        print(f"❌ Researcher agent with tools failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_tool_call():
    """Test a simple tool call to isolate the issue."""
    try:
        from agent.tools.model_tools import ModelTools
        from strands import Agent
        from strands import tool

        print("\n🔧 Testing simple tool call...")

        # Create a simple test tool
        @tool
        def simple_test_tool(message: str) -> str:
            """A simple test tool that returns a message."""
            return f"Tool received: {message}"

        # Create DeepSeek model
        model = ModelTools.create_deepseek_model()
        print("✅ Model created for simple tool test")

        # Create agent with simple tool
        agent = Agent(
            model=model,
            system_prompt="You are a helpful assistant. Use the simple_test_tool when asked.",
            tools=[simple_test_tool],
            callback_handler=None
        )
        print("✅ Agent with simple tool created successfully")

        # Test simple tool call
        print("\n🧪 Testing simple tool call...")
        test_prompt = "Please use the simple_test_tool with the message 'hello world'."
        print(f"📤 Sending prompt: {test_prompt}")
        response = agent(test_prompt)
        print(f"📥 Agent response: {response}")
        print("✅ Simple tool call successful!")

        return True

    except Exception as e:
        print(f"❌ Simple tool call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 DeepSeek Model Test Suite")
    print("=" * 50)

    # Test configuration
    config_ok = test_configuration()

    # Test model creation
    model_ok = test_deepseek_model()

    # Test agent creation (without tools)
    agent_ok = test_agent_creation()

    # Test researcher agent (with tools) - this might fail
    researcher_ok = test_researcher_agent_with_tools()

    # Test researcher agent with actual tool usage - this will likely reproduce the error
    researcher_tools_ok = test_researcher_agent_with_actual_tools()

    # Test simple tool call to isolate the issue
    simple_tool_ok = test_simple_tool_call()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"  Model Creation: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"  Agent Creation: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    print(f"  Researcher Agent: {'✅ PASS' if researcher_ok else '❌ FAIL'}")
    print(f"  Researcher Agent w/ Tools: {'✅ PASS' if researcher_tools_ok else '❌ FAIL'}")
    print(f"  Simple Tool Call: {'✅ PASS' if simple_tool_ok else '❌ FAIL'}")

    if all([config_ok, model_ok, agent_ok]):
        print("\n🎉 Core tests passed! DeepSeek configuration is working correctly.")
        if not researcher_ok:
            print("⚠️  Researcher agent test failed - this might be due to tool compatibility issues.")
        if not researcher_tools_ok:
            print("⚠️  Researcher agent with tools test failed - this reproduces the actual error.")
        if not simple_tool_ok:
            print("⚠️  Simple tool call test failed - this indicates a fundamental tool compatibility issue.")
    else:
        print("\n⚠️  Some core tests failed. Please check the configuration.")
