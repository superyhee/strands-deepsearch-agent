# 网络研究代理系统（Research Agent System）

基于 Strands Agents 构建的多代理研究系统，用于全面的网络研究和信息收集。

## 系统架构

重构后的系统采用模块化设计，具有清晰的关注点分离和责任划分：

```
research_system/
├── core/                # 核心系统组件
│   ├── research_system.py  # 主系统类
│   └── config.py        # 配置管理
├── agents/              # 代理管理
│   └── agent_factory.py # 创建和配置Agent的工厂
├── services/            # 服务层
│   ├── research_service.py  # 研究流程服务
│   ├── analysis_service.py  # 分析服务
│   └── report_service.py    # 报告生成服务
├── tools/               # 工具组件
│   ├── enhanced_search.py   # 增强搜索功能
│   └── web_search.py    # 网络搜索工具
└── utils/               # 工具类
    ├── language_detector.py # 语言检测工具
    ├── search_summary.py    # 搜索摘要处理
    └── reporting_utils.py   # 报告生成工具
```

## 主要组件

### 核心组件

- **ResearchAgentSystem**: 整个研究系统的协调器
- **ResearchConfig**: 系统配置管理

### 代理工厂

- **AgentFactory**: 创建和管理三种不同的代理（研究员、分析员、写作员）

### 服务

- **ResearchService**: 管理研究过程和信息收集
- **AnalysisService**: 负责分析研究结果和识别知识缺口
- **ReportService**: 生成最终研究报告

### 工具类

- **LanguageDetector**: 语言检测和处理
- **SearchSummaryProcessor**: 搜索结果摘要处理
- **ReportFormatter**: 研究报告格式化

## 工作流程

1. **语言检测**: 自动检测查询语言并配置相应的代理
2. **信息收集**: 研究员代理使用增强搜索工具收集信息
3. **质量分析**: 分析员代理评估信息质量并识别知识缺口
4. **额外研究**: 如果需要，进行额外的有针对性的研究
5. **报告生成**: 写作员代理生成最终研究报告

## 技术特点

- **多代理协作**: 使用三个专业代理共同完成研究任务
- **自适应语言**: 自动检测和适应多种语言
- **流式输出**: 支持实时流式生成报告
- **组件化设计**: 清晰的模块分离，易于维护和扩展
