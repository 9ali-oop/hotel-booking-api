"""
MCP (Model Context Protocol) Server for the Hotel Booking Intelligence API.

This module exposes all API endpoints as MCP-compatible tools, allowing
AI assistants (e.g. Claude, ChatGPT) to interact with the hotel booking
data through the emerging Model Context Protocol standard.

The brief states the API should "be demonstrable via local execution,
web hosting (e.g. PythonAnywhere), or a Model Context Protocol (MCP) server."
This file satisfies that MCP requirement.

Usage:
    # Option 1: Run standalone MCP server (SSE transport)
    python mcp_server.py

    # Option 2: The MCP endpoint is also mounted on the main FastAPI app
    #           at /mcp when running via run.py — so any MCP client can
    #           connect to http://localhost:8000/mcp

    # Option 3: Configure in Claude Desktop's claude_desktop_config.json:
    #   {
    #     "mcpServers": {
    #       "hotel-booking-api": {
    #         "url": "http://localhost:8000/mcp"
    #       }
    #     }
    #   }

Author: Ali
Module: COMP3011 Web Services and Web Data
"""

from fastapi_mcp import FastApiMCP
from app.main import app

# Create the MCP server from the existing FastAPI application.
# FastApiMCP introspects all registered routes and exposes them as
# MCP tools — no manual tool definitions needed.
mcp = FastApiMCP(
    app,
    name="Hotel Booking Intelligence MCP",
    description=(
        "MCP server exposing the Hotel Booking Intelligence API. "
        "Provides tools for querying 119,390 hotel booking records, "
        "managing incidents and notes, running analytics, and "
        "performing risk-based insight analysis."
    ),
)

# Mount the MCP server on the FastAPI app at /mcp
# This means when the main app runs, MCP is available at /mcp
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    print("Starting Hotel Booking Intelligence API with MCP support...")
    print("API docs:   http://localhost:8000/docs")
    print("MCP server: http://localhost:8000/mcp")
    uvicorn.run(app, host="0.0.0.0", port=8000)
