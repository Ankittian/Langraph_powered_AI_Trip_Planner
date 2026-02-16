"""FastAPI backend for the AI Trip Planner agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agent.workflow import GraphBuilder
from utils.save_to_document import save_document

import os
import json
import datetime

load_dotenv(override=True)

app = FastAPI(
    title="AI Trip Planner API",
    description="An agentic AI travel planner powered by LangGraph",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    model_provider: str = "google"  # "google" or "groq"


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}


@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    """Invoke the travel-planning agent and return the final answer."""
    try:
        graph = GraphBuilder(model_provider=query.model_provider)
        react_app = graph()

        # Save graph visualisation (best-effort)
        try:
            png_graph = react_app.get_graph().draw_mermaid_png()
            with open("agent_graph.png", "wb") as f:
                f.write(png_graph)
        except Exception:
            pass  # diagram generation is non-critical

        messages = {"messages": [query.question]}
        output = react_app.invoke(messages)

        # Extract the last AI message
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        # Save to file (best-effort)
        try:
            save_document(final_output)
        except Exception:
            pass

        return {"answer": final_output}

    except Exception as e:
        print(f"ERROR: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/query/stream")
async def query_travel_agent_stream(query: QueryRequest):
    """Stream the agent's token-by-token response via Server-Sent Events."""
    try:
        graph = GraphBuilder(model_provider=query.model_provider)
        react_app = graph()

        messages = {"messages": [query.question]}

        async def event_generator():
            try:
                for event in react_app.stream(messages, stream_mode="updates"):
                    for node_name, node_output in event.items():
                        if "messages" in node_output:
                            last_msg = node_output["messages"][-1]
                            # Check if it has tool calls (intermediate step)
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                for tc in last_msg.tool_calls:
                                    data = json.dumps({
                                        "type": "tool_call",
                                        "tool": tc["name"],
                                        "args": str(tc["args"])[:200],
                                    })
                                    yield f"data: {data}\n\n"
                            # Check if it's a tool response
                            elif hasattr(last_msg, "type") and last_msg.type == "tool":
                                data = json.dumps({
                                    "type": "tool_result",
                                    "tool": last_msg.name if hasattr(last_msg, "name") else "tool",
                                    "content": last_msg.content[:500] if last_msg.content else "",
                                })
                                yield f"data: {data}\n\n"
                            else:
                                # Final AI response
                                data = json.dumps({
                                    "type": "response",
                                    "content": last_msg.content if hasattr(last_msg, "content") else str(last_msg),
                                })
                                yield f"data: {data}\n\n"

                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        print(f"ERROR: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})