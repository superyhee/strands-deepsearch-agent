"""FastAPI application for Strands Agent research system."""

import pathlib
import asyncio
from typing import Dict, Any, List, AsyncGenerator
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import fastapi.exceptions
from .research_agent import ResearchAgentSystem
from .configuration import Configuration
# from .simple_research_agent import ResearchAgentSystem

# Define the FastAPI app
app = FastAPI(title="Research Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize configuration from environment variables
config = Configuration.from_runnable_config()

# Initialize the research agent system with auto language detection and config
research_system = ResearchAgentSystem(config=config, language="auto")


class ResearchRequest(BaseModel):
    """Request model for research queries."""
    messages: List[Dict[str, str]]
    max_research_loops: int = 2
    initial_search_query_count: int = 3


class ResearchResponse(BaseModel):
    """Response model for research results."""
    messages: List[Dict[str, str]]
    sources_gathered: List[Dict[str, str]]
    research_metadata: Dict[str, Any]


# @app.post("/research", response_model=ResearchResponse)
# async def conduct_research(request: ResearchRequest):
#     """Conduct research on a given query."""
#     try:
#         print(f"Received request: {request}")

#         # Extract the latest user message
#         user_messages = [msg for msg in request.messages if msg.get("role") == "user"]
#         if not user_messages:
#             raise HTTPException(status_code=400, detail="No user message found")

#         query = user_messages[-1]["content"]
#         print(f"Processing query: {query}")

#         # Conduct research
#         result = research_system.research(
#             query=query,
#             max_research_loops=request.max_research_loops
#         )
#         print(f"Research result: {result}")

#         # Format response
#         response_messages = request.messages + [{
#             "role": "assistant",
#             "content": result["final_report"]
#         }]

#         # Extract sources from research findings
#         sources = []
#         final_report = result.get("final_report", "")
#         if "http" in final_report:
#             # Simple source extraction - could be enhanced
#             lines = final_report.split('\n')
#             for line in lines:
#                 if "URL:" in line:
#                     url = line.split("URL:")[-1].strip()
#                     title = "Research Source"
#                     sources.append({
#                         "label": title,
#                         "value": url,
#                         "short_url": url
#                     })

#         return ResearchResponse(
#             messages=response_messages,
#             sources_gathered=sources,
#             research_metadata={
#                 "research_loops": result.get("research_loops", 1),
#                 "timestamp": result.get("timestamp", ""),
#                 "query": result.get("query", query)
#             }
#         )

#     except Exception as e:
#         print(f"Error in conduct_research: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


async def research_stream_generator(query: str, max_research_loops: int) -> AsyncGenerator[str, None]:
    """Generate streaming research updates."""
    try:
        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'message': 'begining research...', 'progress': 0})}\n\n"

        # Start research with streaming callback
        async for update in research_system.research_stream(
            query=query,
            max_research_loops=max_research_loops
        ):
            yield f"data: {json.dumps(update)}\n\n"

    except Exception as e:
        error_data = {
            'type': 'error',
            'message': f'研究过程中出现错误: {str(e)}',
            'error': str(e)
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@app.post("/research")
async def conduct_research_stream(request: ResearchRequest):
    """Conduct research with streaming updates."""
    try:
        # Extract the latest user message
        user_messages = [msg for msg in request.messages if msg.get("role") == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")

        query = user_messages[-1]["content"]
        print(f"Starting streaming research for query: {query}")

        return StreamingResponse(
            research_stream_generator(query, request.max_research_loops),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )

    except Exception as e:
        print(f"Error in conduct_research_stream: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/quick-research")
# async def quick_research(request: ResearchRequest):
#     """Conduct quick research without multiple loops."""
#     try:
#         user_messages = [msg for msg in request.messages if msg.get("role") == "user"]
#         if not user_messages:
#             raise HTTPException(status_code=400, detail="No user message found")

#         query = user_messages[-1]["content"]
#         result = research_system.quick_research(query)

#         response_messages = request.messages + [{
#             "role": "assistant",
#             "content": result
#         }]

#         return {"messages": response_messages}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend."""
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir
    static_files_path = build_path / "assets"  # Vite uses 'assets' subdir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    build_dir = pathlib.Path(build_dir)

    react = FastAPI(openapi_url="")
    react.mount(
        "/assets", StaticFiles(directory=static_files_path), name="static_assets"
    )

    @react.get("/{path:path}")
    async def handle_catch_all(request: Request, path: str):
        fp = build_path / path
        if not fp.exists() or not fp.is_file():
            fp = build_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    return react


# Mount the frontend under /app
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
