# Research Agent Tool Classes

This directory contains tool classes extracted from the original `research_agent.py` file. These classes provide modular functionality for the research agent system.

## Overview

The original monolithic `ResearchAgentSystem` class has been refactored into several specialized tool classes, each with a specific responsibility:

1. **ModelTools**: For creating and managing Bedrock models
2. **LanguageTools**: For language detection and handling
3. **AgentCreationTools**: For creating and managing research agents
4. **ResearchTools**: For conducting research and analyzing findings
5. **ReportTools**: For generating research reports
6. **Enhanced Search**: For comprehensive web search with multiple fallback options

## Tool Classes

### ModelTools (`model_tools.py`)

Handles the creation and configuration of Bedrock models.

```python
# Example usage
from .tools import ModelTools

model = ModelTools.create_bedrock_model("model_id")
```

### LanguageTools (`language_tools.py`)

Provides functionality for language detection, analysis, and strategy generation.

```python
# Example usage
from .tools import LanguageTools

language_tools = LanguageTools("auto")
detected_language = language_tools.detect_and_set_language(query)
query_type = language_tools.analyze_query_type(query)
```

### AgentCreationTools (`agent_creation_tools.py`)

Creates and configures specialized agents for research, analysis, and report writing.

```python
# Example usage
from .tools import AgentCreationTools

researcher_agent = AgentCreationTools.create_researcher_agent(model, "english")
analyst_agent = AgentCreationTools.create_analyst_agent(model, "english")
writer_agent = AgentCreationTools.create_writer_agent(model, "english")
```

### ResearchTools (`research_tools.py`)

Provides methods for conducting research, analyzing findings, and generating search summaries.

```python
# Example usage
from .tools import ResearchTools

research_findings = ResearchTools.conduct_research_step(researcher_agent, query)
analysis_result = ResearchTools.analyze_findings(analyst_agent, query, research_findings)
needs_more = ResearchTools.needs_additional_research(analysis_result)
```

### ReportTools (`report_tools.py`)

Generates final research reports based on findings and analysis.

```python
# Example usage
from .tools import ReportTools

final_report = ReportTools.generate_final_report(writer_agent, query, analysis, findings)
```

### Enhanced Search (`enhanced_search.py`)

Provides comprehensive web search functionality with multiple fallback options including Tavily, SerpAPI, Google Custom Search, GoogleSearch Library (free), DuckDuckGo, and Wikipedia.

#### Search Methods (in order of preference):
1. **Tavily Search** - Advanced AI-powered search (requires TAVILY_API_KEY)
2. **SerpAPI** - Google search via API (requires SERPAPI_API_KEY)
3. **Google Custom Search** - Official Google API (requires GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID)
4. **GoogleSearch Library** - Free Google search without API keys (requires googlesearch-python package)
5. **DuckDuckGo** - Privacy-focused search
6. **Wikipedia** - Knowledge base search

```python
# Example usage
from .tools import enhanced_web_search, googlesearch_library_search

# Automatic fallback through all search methods
results = enhanced_web_search("research topic", num_results=5)

# Direct GoogleSearch library usage (free alternative to SerpAPI)
results = googlesearch_library_search("粟伟 亚马逊云科技", num_results=5)
```

#### GoogleSearch Library Integration

The system now includes the `googlesearch-python` library as a free alternative to SerpAPI:

```python
# Installation
pip install googlesearch-python

# Direct usage (as mentioned by user)
from googlesearch import search
results = search("粟伟 亚马逊云科技", advanced=True)
for r in results:
    print(r)
```

## Refactored ResearchAgentSystem

A refactored version of the `ResearchAgentSystem` class is available in `research_agent_refactored.py`. This version uses the tool classes to provide the same functionality as the original class but with a more modular and maintainable structure.

```python
# Example usage
from .research_agent_refactored import ResearchAgentSystem

agent_system = ResearchAgentSystem()
result = agent_system.research("What is quantum computing?")
```

## Benefits of the Refactored Code

1. **Modularity**: Each tool class has a specific responsibility, making the code more organized.
2. **Maintainability**: Easier to update and extend specific functionality without affecting other parts.
3. **Reusability**: Tool classes can be used independently in other parts of the application.
4. **Testability**: Easier to write unit tests for specific functionality.
5. **Readability**: Clearer code structure makes it easier to understand the system.
