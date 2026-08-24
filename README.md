# ChatGPT MCP PoC

Minimal **remote MCP server** for testing a custom MCP app from ChatGPT.

It uses the current MCP Python SDK v2 API (`MCPServer`) and Streamable HTTP.

## Included tools

- `ping()` — verifies that the server responds.
- `hello(name)` — simple end-to-end test.
- `search_projects(query, status)` — searches mock corporate data.
- `get_project(project_id)` — returns one mock project.

The mock project functions are intentionally simple. Replace their internals later with calls to your REST APIs, SQL services, CRM, SharePoint gateway, etc.

## 1. Run locally

Requirements: Python 3.10+.

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -e ".[dev]"
python server.py
```

The MCP endpoint will be:

```text
http://localhost:8000/mcp
```

## 2. Test without ChatGPT

Using the MCP Inspector:

```bash
mcp dev server.py
```

Or run the automated tests:

```bash
pytest -q
```

## 3. Run with Docker

```bash
docker build -t chatgpt-mcp-poc .
docker run --rm -p 8000:8000 chatgpt-mcp-poc
```

For a remote hostname:

```bash
docker run --rm \
  -p 8000:8000 \
  -e PUBLIC_HOST=mcp-poc.example.com \
  chatgpt-mcp-poc
```

`PUBLIC_HOST` must contain only the hostname, not `https://` and not `/mcp`.

## 4. Expose it remotely

ChatGPT needs to reach the MCP endpoint. Deploy this container to your normal company infrastructure (Azure Container Apps, App Service, Kubernetes, AWS, GCP, etc.) behind HTTPS.

Example final URL:

```text
https://mcp-poc.example.com/mcp
```

Set this environment variable in the deployment:

```text
PUBLIC_HOST=mcp-poc.example.com
```

The MCP Python SDK protects against DNS rebinding. A remote hostname that is not explicitly allowed can return HTTP 421, so setting `PUBLIC_HOST` is important.

## 5. Register it in ChatGPT

In the ChatGPT workspace with developer mode enabled:

1. Open **Settings / Workspace Settings -> Apps -> Create** (exact menu depends on workspace role).
2. Create a custom MCP app.
3. Enter the remote endpoint, for example:
   `https://mcp-poc.example.com/mcp`
4. For this PoC, use no authentication only if your workspace allows it and the endpoint contains no sensitive data.
5. Select **Scan Tools**.
6. You should see `ping`, `hello`, `search_projects`, and `get_project`.
7. Save the draft app and test it from ChatGPT.

Suggested prompts:

```text
Use the MCP app and call ping.
```

```text
Search the MCP project system for active projects from ACME.
```

```text
Get project P-001 using the MCP app.
```

## 6. Important security note

This repository is a **PoC**, not a production authentication design. It contains only fake data.

Before connecting real corporate systems:

- add OAuth/OIDC or your approved authentication layer;
- authorize each user/action, not only the MCP server globally;
- use least-privilege downstream credentials;
- keep read tools separate from write tools;
- validate tool arguments server-side;
- add audit logs;
- require confirmation/approval for sensitive write actions;
- never expose arbitrary SQL or generic `call_api(url, payload)` tools.

## Repository structure

```text
chatgpt-mcp-poc/
├── server.py
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── tests/
│   └── test_server.py
└── README.md
```

## Next step: connect a real company API

Replace the mock implementation inside a tool, for example:

```python
@mcp.tool()
def get_project(project_id: str) -> dict:
    # Validate project_id
    # Authenticate to the approved internal API
    # GET https://internal-api.example/projects/{project_id}
    # Return a small, controlled response
    ...
```

Keep secrets in the deployment environment or your secret manager, never in the repository.
