"""
Entry point for running the Hotel Booking Intelligence API.

Usage:
    python run.py

The server will start on http://localhost:8000
Interactive API docs available at http://localhost:8000/docs
MCP server available at http://localhost:8000/mcp
"""

import os
import uvicorn

# Import the MCP server module so it mounts on the FastAPI app.
# This makes /mcp available alongside the regular REST endpoints.
try:
    import mcp_server  # noqa: F401 — side-effect import mounts MCP
except ImportError:
    pass  # fastapi-mcp not installed — MCP endpoint simply won't be available

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Auto-reload on code changes during development
    )
