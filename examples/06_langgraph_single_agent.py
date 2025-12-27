"""
Example: LangGraph with Remote A2A Agent

This example demonstrates using LangGraph to orchestrate a workflow that
calls a remote A2A agent as one of its tools/nodes.

This shows how A2A adapters enable integration with other orchestration frameworks.

Prerequisites:
- langgraph and langchain packages installed
- An A2A agent server running (e.g., from example 01)
- OpenAI API key set in environment: OPENAI_API_KEY

Usage:
    # Start an agent server first (e.g., example 01)
    python examples/01_single_n8n_agent.py
    
    # In another terminal, run this LangGraph workflow
    python examples/06_langgraph_single_agent.py
"""

import asyncio
import os
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from a2a.client import A2AClient
from a2a.types import Message, MessageSendParams, TextPart


# Define the graph state
class AgentState(TypedDict):
    """State for the LangGraph workflow."""
    messages: Annotated[list, add_messages]
    result: str


class A2AAgentTool:
    """Tool wrapper for calling an A2A agent from LangGraph."""
    
    def __init__(self, agent_url: str, agent_name: str):
        self.agent_url = agent_url
        self.agent_name = agent_name
        self.client = A2AClient(base_url=agent_url)
    
    async def invoke(self, message: str) -> str:
        """Call the A2A agent with a message."""
        a2a_message = Message(
            role="user",
            content=[TextPart(type="text", text=message)]
        )
        
        params = MessageSendParams(
            messages=[a2a_message],
            session_id="langgraph-session",
        )
        
        try:
            response = await self.client.send_message(params)
            
            if isinstance(response, Message):
                if isinstance(response.content, list):
                    return " ".join([
                        item.text for item in response.content 
                        if hasattr(item, "text")
                    ])
                return str(response.content)
            return str(response)
            
        except Exception as e:
            return f"Error calling {self.agent_name}: {e}"
    
    async def close(self):
        """Close the A2A client."""
        await self.client.close()


async def create_workflow():
    """Create a LangGraph workflow that uses an A2A agent."""
    
    # Initialize the A2A agent tool
    math_agent = A2AAgentTool(
        agent_url="http://localhost:9000",
        agent_name="Math Agent"
    )
    
    # Initialize LLM for orchestration
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Define workflow nodes
    async def analyze_query(state: AgentState) -> AgentState:
        """Analyze the user query to determine if math is needed."""
        last_message = state["messages"][-1]
        query = last_message.content
        
        # Simple check for math-related queries
        math_keywords = ["calculate", "compute", "solve", "math", "+", "-", "*", "/"]
        needs_math = any(keyword in query.lower() for keyword in math_keywords)
        
        if needs_math:
            print("🔍 Query requires mathematical computation")
            return state
        else:
            print("💬 Query doesn't require math, responding directly")
            response = await llm.ainvoke([
                HumanMessage(content=f"Answer this query: {query}")
            ])
            state["result"] = response.content
            return state
    
    async def call_math_agent(state: AgentState) -> AgentState:
        """Call the A2A math agent."""
        last_message = state["messages"][-1]
        query = last_message.content
        
        print(f"🧮 Calling Math Agent: {query}")
        result = await math_agent.invoke(query)
        state["result"] = result
        
        return state
    
    async def format_response(state: AgentState) -> AgentState:
        """Format the final response."""
        print("✅ Formatting final response")
        return state
    
    def should_use_math_agent(state: AgentState) -> str:
        """Decide whether to use the math agent."""
        last_message = state["messages"][-1]
        query = last_message.content
        
        math_keywords = ["calculate", "compute", "solve", "math", "+", "-", "*", "/"]
        needs_math = any(keyword in query.lower() for keyword in math_keywords)
        
        return "math_agent" if needs_math else "format"
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_query)
    workflow.add_node("math_agent", call_math_agent)
    workflow.add_node("format", format_response)
    
    # Add edges
    workflow.set_entry_point("analyze")
    workflow.add_conditional_edges(
        "analyze",
        should_use_math_agent,
        {
            "math_agent": "math_agent",
            "format": "format"
        }
    )
    workflow.add_edge("math_agent", "format")
    workflow.add_edge("format", END)
    
    # Compile
    app = workflow.compile()
    
    return app, math_agent


async def main():
    """Run the LangGraph workflow."""
    
    print("LangGraph + A2A Agent Integration Example")
    print("=" * 50)
    print()
    
    # Create workflow
    app, math_agent = await create_workflow()
    
    # Test queries
    test_queries = [
        "What is 25 * 37 + 18?",
        "Calculate the area of a circle with radius 5",
        "What is the weather today?",  # Non-math query
    ]
    
    try:
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            print("-" * 50)
            
            # Run the workflow
            result = await app.ainvoke({
                "messages": [HumanMessage(content=query)],
                "result": ""
            })
            
            print(f"\n💡 Result: {result['result']}")
            print("=" * 50)
    
    finally:
        # Clean up
        await math_agent.close()


if __name__ == "__main__":
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    # Ensure math agent is running
    print("⚠️  Make sure the Math Agent is running on port 9000")
    print("   (Run: python examples/01_single_n8n_agent.py)")
    print()
    input("Press Enter to continue...")
    print()
    
    asyncio.run(main())

