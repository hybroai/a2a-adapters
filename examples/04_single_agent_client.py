"""
Example: Simple A2A Agent Client

This example demonstrates how to call an A2A agent using the official A2A.
It can be used to test any of the agent servers created with this adapter SDK.

Prerequisites:
- a2a package installed
- An A2A agent server running (e.g., from examples 01-03)

Usage:
    # Start an agent server first (e.g., example 01)
    python examples/01_single_n8n_agent.py
    
    # In another terminal, run this client
    python examples/04_single_agent_client.py
"""

import asyncio

from a2a.client import A2AClient
from a2a.types import Message, MessageSendParams, TextPart


async def main():
    """Call an A2A agent and print the response."""
    
    # Create A2A client pointing to the agent server
    client = A2AClient(base_url="http://localhost:9000")
    
    # Prepare a message
    message = Message(
        role="user",
        content=[
            TextPart(
                type="text",
                text="What is 25 * 37 + 18?"
            )
        ]
    )
    
    params = MessageSendParams(
        messages=[message],
        session_id="example-session-123",
    )
    
    print("Sending message to A2A agent...")
    print(f"Message: {message.content[0].text}")
    print()
    
    try:
        # Send message and get response
        response = await client.send_message(params)
        
        print("Response received:")
        print("-" * 50)
        
        if isinstance(response, Message):
            # Extract text from response content
            if isinstance(response.content, list):
                for item in response.content:
                    if hasattr(item, "text"):
                        print(item.text)
            else:
                print(response.content)
        else:
            # Task response
            print(f"Task created: {response}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()


async def streaming_example():
    """Example of streaming responses from an A2A agent."""
    
    client = A2AClient(base_url="http://localhost:8002")  # LangChain streaming agent
    
    message = Message(
        role="user",
        content=[
            TextPart(
                type="text",
                text="Tell me a short story about AI agents working together."
            )
        ]
    )
    
    params = MessageSendParams(
        messages=[message],
        session_id="streaming-session-456",
    )
    
    print("Sending streaming message to A2A agent...")
    print(f"Message: {message.content[0].text}")
    print()
    print("Streaming response:")
    print("-" * 50)
    
    try:
        async for chunk in client.send_message_stream(params):
            # Print chunks as they arrive
            print(chunk, end="", flush=True)
        print()
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    print("A2A Agent Client Example")
    print("=" * 50)
    print()
    
    # Run non-streaming example
    asyncio.run(main())
    
    print()
    print("=" * 50)
    print()
    
    # Uncomment to test streaming (requires streaming-enabled agent on port 8002)
    # asyncio.run(streaming_example())

