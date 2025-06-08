# AI-Powered Research Assistant with Multi-Agent Architecture

A comprehensive research automation system that leverages multiple specialized AI agents to gather, analyze, and synthesize information from the web, delivering structured research reports in multiple languages.

This project combines a React-based frontend with a Python FastAPI backend to create an intuitive research experience. The system employs a multi-agent architecture with specialized researcher, analyst, and writer agents to deliver thorough and well-structured research reports. The application supports multiple languages, provides real-time progress updates, and offers configurable research depth levels.

## Repository Structure
```
.
├── backend/                      # Python FastAPI backend application
│   ├── src/agent/               # Core agent implementation
│   │   ├── tools/               # Agent tools for search, analysis, and report generation
│   │   └── utils/               # Utility functions and language detection
├── frontend/                    # React TypeScript frontend application
│   ├── src/                     # Frontend source code
│   │   ├── components/          # React components including UI elements
│   │   ├── hooks/              # Custom React hooks for research agent integration
│   │   └── lib/                # Utility functions and shared code
└── docker-compose.yml          # Docker composition for Redis, PostgreSQL, and API services
```

## Usage Instructions
### Prerequisites
- Docker and Docker Compose
- Node.js 20.x or later
- Python 3.11 or later
- AWS credentials for Bedrock API access
- Optional: Google Search API credentials (falls back to DuckDuckGo if not provided)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Backend setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -e .
```

3. Frontend setup:
```bash
cd frontend
npm install
```

4. Environment configuration:
```bash
# Create .env file in backend directory
cp .env.example .env
# Add your AWS credentials and optional API keys
```

### Quick Start

1. Start the services using Docker Compose:
```bash
docker-compose up -d
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Access the application at http://localhost:5173/app

### More Detailed Examples

1. Basic Research Query:
```typescript
// Submit a research query with low effort level
await researchAgent.submit({
  messages: [{
    type: "human",
    content: "What are the latest developments in quantum computing?"
  }],
  initial_search_query_count: 1,
  max_research_loops: 1
});
```

2. Deep Research with Multiple Sources:
```typescript
// Submit a research query with high effort level
await researchAgent.submit({
  messages: [{
    type: "human",
    content: "Analyze the impact of artificial intelligence on healthcare"
  }],
  initial_search_query_count: 5,
  max_research_loops: 3
});
```

### Troubleshooting

1. Backend Connection Issues:
- Error: "Failed to connect to backend API"
- Solution: 
  ```bash
  # Check if backend is running
  curl http://localhost:8000/health
  # Verify environment variables
  cat backend/.env
  ```

2. Search API Issues:
- Error: "Search API not responding"
- Solution: Check API keys in environment variables and verify rate limits

## Data Flow
The system processes research requests through a multi-stage pipeline, coordinating between specialized AI agents for comprehensive results.

```ascii
[User Input] -> [Frontend] -> [FastAPI Backend] -> [Research Agent]
                                                      |
                                                      v
[Final Report] <- [Writer Agent] <- [Analyst Agent] <- [Web Search/Analysis]
```

Key component interactions:
1. Frontend submits research requests to FastAPI backend
2. Research Agent generates optimized search queries
3. Web searches are conducted with fallback options
4. Analyst Agent verifies and synthesizes information
5. Writer Agent generates structured final report
6. Real-time updates streamed to frontend via SSE
7. Results cached in Redis for performance

## Infrastructure

![Infrastructure diagram](./docs/infra.svg)

### Redis
- Type: Cache Service
- Purpose: Temporary data storage and caching
- Configuration: Default port 6379

### PostgreSQL
- Type: Database Service
- Purpose: Persistent data storage
- Port: 5433 (mapped from 5432)
- Credentials: 
  - Database: postgres
  - User: postgres
  - Password: postgres

### API Service
- Type: Docker Container
- Image: claude-fullstack-strands-agent
- Port: 8123 (mapped from 8000)
- Dependencies: Redis and PostgreSQL services
- Environment Variables:
  - AWS credentials
  - Search API keys
  - Database connections