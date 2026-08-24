from __future__ import annotations

import os
from typing import Any

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings


mcp = MCPServer("Company MCP PoC")

# Mock data: replace this with calls to your company's APIs/databases later.
PROJECTS = [
    {
        "id": "P-001",
        "name": "Demo Solar Project",
        "client": "ACME Energy",
        "status": "active",
        "country": "Colombia",
    },
    {
        "id": "P-002",
        "name": "Demo Efficiency Project",
        "client": "Globex",
        "status": "review",
        "country": "Spain",
    },
]


@mcp.tool()
def ping() -> dict[str, str]:
    """Check that the MCP server is reachable and responding."""
    return {"status": "ok", "server": "Company MCP PoC"}


@mcp.tool()
def hello(name: str) -> dict[str, str]:
    """Return a simple greeting. Useful for the first end-to-end ChatGPT test."""
    return {"message": f"Hello, {name}. Your MCP connection is working."}


@mcp.tool()
def search_projects(query: str = "", status: str | None = None) -> list[dict[str, Any]]:
    """Search demo projects by free text and optionally filter by status.

    Args:
        query: Text matched against project id, name, client, country, or status.
        status: Optional exact project status, for example 'active' or 'review'.
    """
    q = query.strip().lower()
    wanted_status = status.strip().lower() if status else None

    results: list[dict[str, Any]] = []
    for project in PROJECTS:
        if wanted_status and str(project["status"]).lower() != wanted_status:
            continue

        haystack = " ".join(str(value) for value in project.values()).lower()
        if q and q not in haystack:
            continue

        results.append(project)

    return results


@mcp.tool()
def get_project(project_id: str) -> dict[str, Any]:
    """Get one demo project by its exact project id."""
    for project in PROJECTS:
        if project["id"].lower() == project_id.strip().lower():
            return project

    return {
        "found": False,
        "project_id": project_id,
        "message": "Project not found",
    }


def build_transport_security() -> TransportSecuritySettings:
    """Build the HTTP Host allowlist used by the MCP SDK.

    For a remote deployment, set PUBLIC_HOST to the hostname only, for example:
    mcp-poc.example.com
    """
    public_host = os.getenv("PUBLIC_HOST", "").strip()

    if public_host:
        return TransportSecuritySettings(
            allowed_hosts=[public_host, f"{public_host}:*"],
        )

    # Safe local defaults. A real remote deployment should set PUBLIC_HOST.
    return TransportSecuritySettings(
        allowed_hosts=[
            "localhost",
            "localhost:*",
            "127.0.0.1",
            "127.0.0.1:*",
            "[::1]",
            "[::1]:*",
        ],
    )


# ASGI app. The MCP endpoint is /mcp.
app = mcp.streamable_http_app(
    json_response=True,
    stateless_http=True,
    transport_security=build_transport_security(),
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )
