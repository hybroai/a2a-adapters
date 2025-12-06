#!/usr/bin/env python3
"""
A2A Agent Startup Script

Usage:
    python start_agent.py n8n      # Start n8n agent
    python start_agent.py crewai   # Start crewai agent
    python start_agent.py langchain # Start langchain agent

Environment variables:
    N8N_WEBHOOK_URL - n8n webhook URL (default: https://n8n.example.com/webhook/math-agent)
"""

import asyncio
import sys
import os

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_n8n_agent():
    """Start N8n Agent"""
    print("🚀 Starting N8n Agent...")
    exec(open("examples/01_single_n8n_agent.py").read(), {"__name__": "__main__"})

def start_crewai_agent():
    """Start CrewAI Agent"""
    print("🚀 Starting CrewAI Agent...")
    exec(open("examples/02_single_crewai_agent.py").read(), {"__name__": "__main__"})

def start_langchain_agent():
    """Start LangChain Agent"""
    print("🚀 Starting LangChain Agent...")
    exec(open("examples/03_single_langchain_agent.py").read(), {"__name__": "__main__"})

def main():
    if len(sys.argv) < 2:
        print("Usage: python start_agent.py <agent_type>")
        print("Supported agent types: n8n, crewai, langchain")
        sys.exit(1)

    agent_type = sys.argv[1].lower()

    try:
        if agent_type == "n8n":
            start_n8n_agent()
        elif agent_type == "crewai":
            start_crewai_agent()
        elif agent_type == "langchain":
            start_langchain_agent()
        else:
            print(f"Unknown agent type: {agent_type}")
            print("Supported types: n8n, crewai, langchain")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Agent stopped")
    except Exception as e:
        print(f"Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
