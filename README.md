# Research Intelligence Server

A production-grade MCP (Model Context Protocol) server that exposes research paper intelligence through tools, resources, and prompts.

Built as a companion implementation to the article series:
- **Part 1:** [MCP Design Patterns for Production Agentic Systems](https://medium.com/@shubhodaya.hampiholi/mcp-design-patterns-for-production-agentic-systems-b42c9fdb4b24)
- **Part 2:** [MCP Internals: Protocol Mechanics, Primitives, and Implementation](https://medium.com/@shubhodaya.hampiholi/mcp-internals-protocol-mechanics-primitives-and-implementation-72d84fdb33e9)

---

## What This Server Does

The server exposes a curated collection of 12 research papers across 4 domains (machine learning, NLP, distributed systems, computer vision) via three MCP primitives:

**Tools** — model-invoked actions:
- `search_papers` — search by topic, domain, year range, or citation threshold
- `get_citation_network` — traverse the citation graph to a specified depth and direction
- `compare_papers` — structured comparison of 2–4 papers across specified dimensions
- `get_domain_statistics` — analytical statistics for a research domain

**Resources** — URI-addressed data:
- `research://papers` — full paper index (metadata only)
- `research://domains` — domain index with paper counts and top tags
- `research://papers/{paper_id}` — individual paper with full text
- `research://papers/{paper_id}/citations` — flat citation list for a paper

**Prompts** — reusable interaction templates:
- `literature_review` — structured literature review on a topic
- `paper_critique` — rigorous academic critique of a specific paper
- `research_gap_analysis` — gap analysis for a research domain

---

## Project Structure

## Project Structure

```
src/research_server/
├── models/
│   └── domain.py              # Pydantic domain models — the living contract
├── data/
│   ├── papers.py              # Static mock dataset (12 papers)
│   └── store.py               # Data access layer
├── primitives/
│   ├── resources.py           # Resource handlers
│   ├── tools.py               # Tool handlers
│   └── prompts.py             # Prompt handlers
├── server.py                  # Transport-agnostic server assembly
├── transport/
│   ├── stdio.py               # stdio transport runner
│   └── http.py                # Streamable HTTP transport runner
└── observability/
    └── logging.py             # Structured JSON logging (stderr only)
```

---

## Transports

### stdio (for local clients — Claude Desktop, Cursor, etc.)

```bash
uv run research-server-stdio
```

### Streamable HTTP (for networked/remote clients)

```bash
uv run research-server-http
```

Server starts at `http://127.0.0.1:8000/mcp/` by default.

Environment variables: `HOST`, `PORT`, `LOG_LEVEL`

---

## Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "research-intelligence-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/research-intelligence-server",
        "research-server-stdio"
      ]
    }
  }
}
```

Restart Claude Desktop. The server's tools and prompts will appear in the interface.

---

## Verify the Server

### stdio
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | uv run research-server-stdio 2>/dev/null
```

### Streamable HTTP
```bash
# Terminal 1 — start the server
uv run research-server-http

# Terminal 2 — send initialize request
curl -L -X POST http://127.0.0.1:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
```

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/research-intelligence-server.git
cd research-intelligence-server
uv sync
```

### Run tests

```bash
uv run pytest tests/ -v
```

### Run stdio server

```bash
uv run research-server-stdio
```

### Run HTTP server

```bash
uv run research-server-http
```

---

## Design Principles

- **Transport-agnostic server** — `server.py` is identical across both transports
- **Enums over booleans** — all semantic values use enums for LLM reasoning clarity
- **Two error levels** — protocol errors vs application errors (`isError=True`)
- **`Paper` vs `PaperSummary`** — collections never return full text accidentally
- **Structured logging to stderr** — stdout is the protocol channel in stdio transport
- **Data access through store** — primitives never import raw data directly

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
