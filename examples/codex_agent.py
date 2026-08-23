"""
Example: OpenAI Codex as A2A Agent

Expose the OpenAI Codex CLI as an A2A-compatible agent.

Prerequisites:
- Codex CLI installed: npm install -g @openai/codex
- OPENAI_API_KEY set in environment

Security:
    By default, bypass_approvals and skip_git_check are disabled. To enable
    for trusted, sandboxed environments only:

        # Option 1: constructor arguments
        adapter = CodexAdapter(
            working_dir=...,
            bypass_approvals=True,   # disables sandboxing and approval prompts
            skip_git_check=True,     # allows running outside git repos
        )

        # Option 2: environment variables (zero-code migration)
        A2A_CODEX_BYPASS_APPROVALS=1 A2A_CODEX_SKIP_GIT_CHECK=1 \
            python examples/codex_agent.py

Usage:
    python examples/codex_agent.py
    python examples/codex_agent.py /path/to/project
    # Agent card at http://localhost:9011/.well-known/agent-card.json
"""

import os
import sys

from a2a_adapter import CodexAdapter, serve_agent

working_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

adapter = CodexAdapter(
    working_dir=working_dir,
    timeout=600,
    name="Codex Agent",
    description="OpenAI Codex CLI coding agent",
    # Uncomment for trusted, sandboxed environments only:
    # bypass_approvals=True,
    # skip_git_check=True,
)

print("Starting Codex A2A agent...")
print(f"  Working directory: {working_dir}")
print(f"  Bypass approvals: {adapter.bypass_approvals}")
print(f"  Skip git check: {adapter.skip_git_check}")
print("  Agent card: http://localhost:9011/.well-known/agent-card.json")

serve_agent(adapter, port=9011)
