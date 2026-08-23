"""
Example: Claude Code as A2A Agent

Expose the Claude Code CLI as an A2A-compatible agent.

Prerequisites:
- Claude Code CLI installed: npm install -g @anthropic-ai/claude-code
- ANTHROPIC_API_KEY set in environment

Security:
    By default, skip_permissions is disabled. Without it (and without a
    pre-configured Claude Code permissions file), tool-use calls may not
    proceed in unattended mode. To enable full-trust mode for trusted,
    sandboxed environments only:

        # Option 1: constructor argument
        adapter = ClaudeCodeAdapter(working_dir=..., skip_permissions=True)

        # Option 2: environment variable (zero-code migration)
        A2A_CLAUDE_SKIP_PERMISSIONS=1 python examples/claude_code_agent.py

Usage:
    python examples/claude_code_agent.py
    python examples/claude_code_agent.py /path/to/project
    # Agent card at http://localhost:9010/.well-known/agent-card.json
"""

import os
import sys

from a2a_adapter import ClaudeCodeAdapter, serve_agent

working_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

adapter = ClaudeCodeAdapter(
    working_dir=working_dir,
    timeout=600,
    name="Claude Code Agent",
    description="Claude Code AI coding agent — code generation, debugging, refactoring",
    # Uncomment for trusted, sandboxed environments only:
    # skip_permissions=True,
)

print("Starting Claude Code A2A agent...")
print(f"  Working directory: {working_dir}")
print(f"  Skip permissions: {adapter.skip_permissions}")
print("  Agent card: http://localhost:9010/.well-known/agent-card.json")

serve_agent(adapter, port=9010)
