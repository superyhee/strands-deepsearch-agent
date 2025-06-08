# 代码重构迁移指南

本指南介绍如何从原始的`ResearchAgentSystem`类迁移到重构后的模块化系统。

## 迁移概述

原始代码将所有功能都集中在一个大型`ResearchAgentSystem`类中，新的架构将其拆分为多个专注于特定功能的模块。

### 主要变更

1. **模块化结构**: 将单一类拆分为多个模块和类
2. **关注点分离**: 每个模块负责特定功能
3. **配置集中化**: 通过`ResearchConfig`统一管理配置
4. **代理工厂模式**: 通过`AgentFactory`创建和管理代理

## 导入方式变更

### 原始代码

```python
from backend.src.agent.research_agent import ResearchAgentSystem
```

### 重构后代码

```python
from research_system import ResearchAgentSystem, ResearchConfig
```

## 初始化方式变更

### 原始代码

```python
agent = ResearchAgentSystem(
    config=Configuration(),
    language="auto"
)
```

### 重构后代码

```python
config = ResearchConfig(
    query_generator_model="anthropic.claude-3-sonnet-20240229-v1:0",
    reflection_model="anthropic.claude-3-sonnet-20240229-v1:0",
    answer_model="anthropic.claude-3-opus-20240229-v1:0",
    max_research_loops=2
)
agent = ResearchAgentSystem(config=config, language="auto")
```

## 功能对应关系

| 原始代码方法                    | 重构后代码方法                | 所在模块              |
| ------------------------------- | ----------------------------- | --------------------- |
| `_create_bedrock_model`         | `_create_bedrock_model`       | `AgentFactory`        |
| `_create_researcher_agent`      | `_create_researcher_agent`    | `AgentFactory`        |
| `_create_analyst_agent`         | `_create_analyst_agent`       | `AgentFactory`        |
| `_create_writer_agent`          | `_create_writer_agent`        | `AgentFactory`        |
| `_detect_and_set_language`      | `_detect_and_set_language`    | `ResearchAgentSystem` |
| `_conduct_research_step`        | `conduct_research`            | `ResearchService`     |
| `_analyze_findings`             | `analyze_findings`            | `AnalysisService`     |
| `_needs_additional_research`    | `needs_additional_research`   | `AnalysisService`     |
| `_conduct_additional_research`  | `conduct_additional_research` | `ResearchService`     |
| `_generate_final_report`        | `generate_report`             | `ReportService`       |
| `_generate_final_report_stream` | `generate_report_stream`      | `ReportService`       |
| `research`                      | `research`                    | `ResearchAgentSystem` |
| `research_stream`               | `research_stream`             | `ResearchAgentSystem` |

## 自定义设置示例

### 使用自定义配置

```python
from research_system import ResearchAgentSystem, ResearchConfig

# 自定义配置
config = ResearchConfig(
    query_generator_model="anthropic.claude-3-haiku-20240307-v1:0",  # 使用更轻量的模型
    reflection_model="anthropic.claude-3-haiku-20240307-v1:0",
    answer_model="anthropic.claude-3-sonnet-20240229-v1:0",
    max_research_loops=3  # 增加研究循环次数
)

# 初始化系统
agent = ResearchAgentSystem(config=config, language="chinese")

# 执行研究
result = agent.research("量子计算的最新进展")
```

### 使用流式输出

```python
from research_system import ResearchAgentSystem
import asyncio

async def stream_research():
    agent = ResearchAgentSystem(language="auto")

    async for update in agent.research_stream("人工智能在医疗领域的应用"):
        if update['type'] == 'report_chunk':
            print(update['data']['chunk'], end='')
        elif update['type'] == 'complete':
            print("\n\n研究完成!")

# 运行异步函数
asyncio.run(stream_research())
```

## 注意事项

1. 重构后的代码保持了与原始代码相同的功能和 API 接口
2. 如果您的代码依赖于原始类的内部方法，需要调整为使用新的服务类中的方法
3. 配置对象结构发生了变化，从`Configuration`改为`ResearchConfig`
