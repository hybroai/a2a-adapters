# Quick Start Guide

Get your first A2A agent running in under 5 minutes.

This guide covers two ways to expose an agent: a thin CLI for supported local
agent executables, and the Python SDK for frameworks and custom integrations.

## Prerequisites

- Python 3.11+
- For the CLI path: Pi, Codex, Claude, or OpenClaw installed locally
- For the SDK path: an n8n workflow, CrewAI crew, LangChain chain, LangGraph
  workflow, local agent, or custom function

## Step 1: Install

```bash
pip install a2a-adapter
```

For specific frameworks:

```bash
pip install a2a-adapter[crewai]        # CrewAI
pip install a2a-adapter[langchain]     # LangChain
pip install a2a-adapter[langgraph]     # LangGraph
pip install a2a-adapter[all]           # Everything
```

## Option 1: Start a Local Agent with the CLI

Run the command from the project directory the agent should use:

```bash
a2a-adapter pi --port 9012
a2a-adapter codex --port 9011
a2a-adapter claude --port 9010
a2a-adapter openclaw --port 9008
```

Use `--cwd /path/to/project` to select another directory. A2A server options
go before `--`; native agent options go after it:

```bash
a2a-adapter pi --port 9012 -- --model <model> --thinking high
a2a-adapter codex --port 9011 -- --model <model> --sandbox workspace-write
a2a-adapter claude --port 9010 -- --model <model>
a2a-adapter openclaw --port 9008 --agent-id main --thinking high
```

Run `a2a-adapter -help` to list supported agents, or
`a2a-adapter <agent> -help` for agent-specific options. Hermes is available as
a Python SDK adapter but is not supported by the v1 CLI.

## Option 2: Create an Agent with the Python SDK

Choose your framework — every example follows the same 3-line pattern: **import**, **adapter**, **serve**.

### Option A: n8n Workflow

```python
# my_agent.py
from a2a_adapter import N8nAdapter, serve_agent

adapter = N8nAdapter(
    webhook_url="https://your-n8n.com/webhook/workflow-id",
    name="My N8n Agent",
    description="My n8n workflow as an A2A agent",
)
serve_agent(adapter, port=9000)
```

### Option B: LangChain Chain (with streaming)

```python
# my_agent.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from a2a_adapter import LangChainAdapter, serve_agent

chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("user", "{input}"),
    ])
    | ChatOpenAI(model="gpt-4o-mini", streaming=True)
)

adapter = LangChainAdapter(runnable=chain, input_key="input", name="Chat Agent")
serve_agent(adapter, port=9000)  # Streaming auto-detected!
```

### Option C: LangGraph Workflow (with streaming)

```python
# my_agent.py
from a2a_adapter import LangGraphAdapter, serve_agent

graph = build_my_graph().compile()  # Your LangGraph CompiledGraph

adapter = LangGraphAdapter(
    graph=graph,
    name="Research Agent",
    description="LangGraph research workflow as an A2A agent",
)
serve_agent(adapter, port=9000)
```

### Option D: CrewAI Crew

```python
# my_agent.py
from crewai import Agent, Crew, Process
from a2a_adapter import CrewAIAdapter, serve_agent

crew = Crew(agents=[...], tasks=[...], process=Process.sequential)

adapter = CrewAIAdapter(crew=crew, name="Research Crew", timeout=600)
serve_agent(adapter, port=9000)
```

### Option E: OpenClaw Agent

```python
# my_agent.py
from a2a_adapter import OpenClawAdapter, serve_agent

adapter = OpenClawAdapter(thinking="low", name="OpenClaw Agent")
serve_agent(adapter, port=9000)
```

### Option F: Ollama (Local LLM)

```python
# my_agent.py
from a2a_adapter import OllamaAdapter, serve_agent
from a2a_adapter.integrations.ollama import OllamaClient

client = OllamaClient(model="llama3.2")
adapter = OllamaAdapter(client=client, name="Local LLM Agent")
serve_agent(adapter, port=9000)
```

### Option G: Custom Function

```python
# my_agent.py
from a2a_adapter import CallableAdapter, serve_agent

async def my_agent(inputs: dict) -> str:
    return f"Echo: {inputs['message']}"

adapter = CallableAdapter(func=my_agent, name="Echo Agent")
serve_agent(adapter, port=9000)
```

### Option H: Custom Adapter Class

For full control, subclass `BaseA2AAdapter`:

```python
# my_agent.py
from a2a_adapter import BaseA2AAdapter, AdapterMetadata, serve_agent

class MyAdapter(BaseA2AAdapter):
    async def invoke(self, user_input: str, context_id: str | None = None, **kwargs) -> str:
        return f"You said: {user_input}"

    def get_metadata(self) -> AdapterMetadata:
        return AdapterMetadata(name="My Agent", description="Custom A2A agent")

serve_agent(MyAdapter(), port=9000)
```

### Run Your SDK Agent

```bash
python my_agent.py
```

Your agent is now running at `http://localhost:9000`.

The A2A SDK automatically:
- Generates an **AgentCard** from your adapter metadata
- Serves it at `/.well-known/agent-card.json` (with the legacy
  `/.well-known/agent.json` alias)
- Handles **task management**, **JSON-RPC 2.0**, and **SSE streaming**

## Test Either Kind of Agent

### Using curl

```bash
# Fetch the auto-generated agent card
curl http://localhost:9000/.well-known/agent-card.json

# Send a message via JSON-RPC 2.0
curl -X POST http://localhost:9000 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "messageId": "msg-1",
        "parts": [{"kind": "text", "text": "Hello!"}]
      }
    }
  }'
```

### Using the example client

```bash
python examples/single_agent_client.py
```

### Using httpx (Python)

```python
import asyncio, httpx

async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        # Fetch agent card
        card = (await client.get("http://localhost:9000/.well-known/agent-card.json")).json()
        print(f"Agent: {card['name']}")

        # Send a message
        resp = await client.post("http://localhost:9000", json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "messageId": "msg-1",
                    "parts": [{"kind": "text", "text": "Hello!"}],
                }
            },
        })
        print(resp.json())

asyncio.run(main())
```

## What's Next?

### Supported Python SDK Adapters

| Framework | Adapter | Streaming |
|---|---|---|
| n8n | `N8nAdapter` | - |
| LangChain | `LangChainAdapter` | Auto-detected |
| LangGraph | `LangGraphAdapter` | Auto-detected |
| CrewAI | `CrewAIAdapter` | - |
| Claude Code | `ClaudeCodeAdapter` | Yes |
| Codex | `CodexAdapter` | - |
| OpenClaw | `OpenClawAdapter` | - |
| Ollama | `OllamaAdapter` | Yes |
| Pi | `PiAdapter` | Yes |
| Hermes | `HermesAdapter` | Yes |
| Any function | `CallableAdapter` | Optional |
| Custom class | `BaseA2AAdapter` | Optional |

### Advanced Usage

#### ASGI Deployment (Gunicorn / Hypercorn)

```python
from a2a_adapter import N8nAdapter, to_a2a

adapter = N8nAdapter(webhook_url="http://localhost:5678/webhook/agent")
app = to_a2a(adapter)  # Returns Starlette ASGI app

# Deploy: gunicorn app:app -k uvicorn.workers.UvicornWorker
```

#### Register a Third-party Adapter

```python
from a2a_adapter import register_adapter, BaseA2AAdapter

@register_adapter("my_framework")
class MyFrameworkAdapter(BaseA2AAdapter):
    async def invoke(self, user_input, context_id=None, **kwargs):
        return "Hello from my framework!"
```

### Next Steps

1. **Explore examples** — See [examples/](examples/) for complete working code
2. **Read the API** — See [README.md](README.md) for full API reference
3. **Understand the design** — See [ARCHITECTURE.md](ARCHITECTURE.md) for the layered architecture
4. **Build multi-agent systems** — Connect multiple A2A agents together
5. **Create custom adapters** — Integrate your own frameworks

## Troubleshooting

**Import errors:**

```bash
pip install a2a-adapter[langchain]  # Or [crewai], [langgraph], [all]
```

**Port already in use:**

```bash
lsof -i :9000           # Find the process
kill <PID>              # Kill it
# Or use a different port:
serve_agent(adapter, port=8001)
```

**Missing API keys (LangChain / CrewAI):**

```bash
export OPENAI_API_KEY="sk-..."
```

For development setup, test commands, and debugging guidance, see
[CONTRIBUTING.md](CONTRIBUTING.md#development-setup).

## Additional Resources

- [Full Documentation](README.md) — Complete API reference
- [Architecture Guide](ARCHITECTURE.md) — Design and implementation details
- [Examples](examples/) — Complete working examples
- [Contributing](CONTRIBUTING.md) — Development setup and contribution guide
