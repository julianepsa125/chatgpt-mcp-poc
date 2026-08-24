import pytest
from mcp import Client

from server import mcp


@pytest.mark.anyio
async def test_ping() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool("ping", {})
        assert result.structured_content == {
            "result": {"status": "ok", "server": "Company MCP PoC"}
        }


@pytest.mark.anyio
async def test_search_projects() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "search_projects", {"query": "ACME", "status": "active"}
        )
        projects = result.structured_content["result"]
        assert len(projects) == 1
        assert projects[0]["id"] == "P-001"
