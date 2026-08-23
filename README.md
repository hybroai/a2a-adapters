# A2A Adapter

[![PyPI version](https://badge.fury.io/py/a2a-adapter.svg)](https://badge.fury.io/py/a2a-adapter)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Expose your AI agent as an A2A Protocol server in a few lines of Python.**

`a2a-adapter` wraps agent CLIs, local agents, workflow engines, and Python agent
frameworks behind the [A2A (Agent-to-Agent) Protocol](https://github.com/a2aproject/A2A).
It handles AgentCard generation, JSON-RPC, task lifecycle, and streaming through
the official A2A SDK, so your adapter only needs to invoke the underlying agent.

Works with Claude Code, Codex, Pi, OpenClaw, n8n, LangGraph, LangChain,
CrewAI, Ollama, Hermes Agent, and custom Python functions.

## Install

```bash
pip install a2a-adapter
```

## CLI Use Case

Use the CLI when you want to expose an already installed local agent from the
current terminal directory without writing Python:

```bash
a2a-adapter pi --port 9012
a2a-adapter codex --port 9011
a2a-adapter claude --port 9010
a2a-adapter openclaw --port 9008
```

Options before `--` configure the A2A server. Options after `--` are passed
to the underlying agent CLI:

```bash
a2a-adapter pi --port 9012 -- --model <model> --thinking high
a2a-adapter codex --port 9011 -- --model <model> --sandbox workspace-write
a2a-adapter claude --port 9010 -- --model <model>
a2a-adapter openclaw --port 9008 --agent-id main --thinking high
```

Use `--cwd /path/to/project` to choose another working directory and
`--host 0.0.0.0` when the server must be reachable outside the local machine.
Pi source commands can be selected without a shell wrapper:

```bash
A2A_PI_COMMAND='npx tsx /path/to/pi/packages/coding-agent/src/cli.ts' \
  a2a-adapter pi --port 9012
```

Run `a2a-adapter -help` for the supported agents, or
`a2a-adapter <agent> -help` for agent-specific usage.
The adapter owns protocol and session flags such as Pi's `--mode rpc` and
Codex's `--json`; those flags cannot be overridden after `--`.

## Python SDK Use Case

Use the Python SDK when embedding A2A support in an application, wrapping a
Python framework, or providing custom adapter configuration:

```python
from a2a_adapter import CallableAdapter, serve_agent

adapter = CallableAdapter(func=lambda inputs: f"Echo: {inputs['message']}", name="Echo")
serve_agent(adapter, port=9000)
```

The SDK produces the same A2A server and auto-generated AgentCard:

```text
http://localhost:9000/.well-known/agent-card.json
```

## Supported Python SDK Adapters

| Framework or agent | Adapter | Streaming | Example |
|---|---|---:|---|
| Claude Code | `ClaudeCodeAdapter` | Yes | [claude_code_agent.py](examples/claude_code_agent.py) |
| Codex | `CodexAdapter` | No | [codex_agent.py](examples/codex_agent.py) |
| Pi | `PiAdapter` | Yes | [pi_agent.py](examples/pi_agent.py) |
| OpenClaw | `OpenClawAdapter` | No | [openclaw_agent.py](examples/openclaw_agent.py) |
| n8n | `N8nAdapter` | No | [n8n_agent.py](examples/n8n_agent.py) |
| LangGraph | `LangGraphAdapter` | Yes | [langgraph_server.py](examples/langgraph_server.py) |
| LangChain | `LangChainAdapter` | Yes | [langchain_agent.py](examples/langchain_agent.py) |
| CrewAI | `CrewAIAdapter` | No | [crewai_agent.py](examples/crewai_agent.py) |
| Ollama | `OllamaAdapter` | Yes | [ollama_agent.py](examples/ollama_agent.py) |
| Hermes Agent | `HermesAdapter` | Yes | [hermes_agent.py](examples/hermes_agent.py) |
| Python callable | `CallableAdapter` | Optional | [quickstart.py](examples/quickstart.py) |
| Custom class | `BaseA2AAdapter` | Optional | [custom_adapter.py](examples/custom_adapter.py) |

## Documentation

- [Quick Start](QUICKSTART.md) - end-to-end setup and testing guide
- [Examples](examples/README.md) - runnable examples for each adapter
- [Architecture](ARCHITECTURE.md) - SDK delegation, request flow, and internals
- [Changelog](CHANGELOG.md) - release notes and migration history
- [Contributing](CONTRIBUTING.md) - development setup and contribution guide

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hybroai/a2a-adapter&type=Date&legend=top-left&v=2)](https://www.star-history.com/?repos=hybroai%2Fa2a-adapter&type=date&legend=top-left)

## License

Apache-2.0 - see [LICENSE](LICENSE).

Built by [HYBRO AI](https://hybro.ai). Powered by the
[A2A Protocol](https://github.com/a2aproject/A2A).
