"""
n8n adapter for A2A Protocol.

This adapter enables n8n workflows to be exposed as A2A-compliant agents
by forwarding A2A messages to n8n webhooks.
"""

import json
from typing import Any, Dict

import httpx
from a2a.types import Message, MessageSendParams, Task, TextPart

from ..adapter import BaseAgentAdapter


class N8nAgentAdapter(BaseAgentAdapter):
    """
    Adapter for integrating n8n workflows as A2A agents.
    
    This adapter forwards A2A message requests to an n8n webhook URL and
    translates the response back to A2A format.
    """

    def __init__(
        self,
        webhook_url: str,
        timeout: int = 30,
        headers: Dict[str, str] | None = None,
    ):
        """
        Initialize the n8n adapter.
        
        Args:
            webhook_url: The n8n webhook URL to send requests to
            timeout: HTTP request timeout in seconds (default: 30)
            headers: Optional additional HTTP headers to include in requests
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.headers = headers or {}
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def handle(self, params: MessageSendParams) -> Message | Task:
        """Handle a non-streaming A2A message request."""
        framework_input = await self.to_framework(params)
        framework_output = await self.call_framework(framework_input, params)
        return await self.from_framework(framework_output, params)

    async def to_framework(self, params: MessageSendParams) -> Dict[str, Any]:
        """
        Convert A2A message parameters to n8n webhook payload format.
        
        Extracts the user's message text and constructs a JSON payload
        suitable for posting to an n8n webhook.
        
        Args:
            params: A2A message parameters
            
        Returns:
            Dictionary with 'message' and optional 'metadata' keys
        """
        # Extract text from the last user message
        user_message = ""
        if params.messages:
            last_message = params.messages[-1]
            if hasattr(last_message, "content"):
                if isinstance(last_message.content, list):
                    # Extract text from content blocks
                    text_parts = [
                        item.text
                        for item in last_message.content
                        if hasattr(item, "text")
                    ]
                    user_message = " ".join(text_parts)
                elif isinstance(last_message.content, str):
                    user_message = last_message.content

        # Build n8n webhook payload
        payload = {
            "message": user_message,
            "metadata": {
                "session_id": getattr(params, "session_id", None),
                "context": getattr(params, "context", None),
            },
        }

        return payload

    async def call_framework(
        self, framework_input: Dict[str, Any], params: MessageSendParams
    ) -> Dict[str, Any]:
        """
        Execute the n8n workflow by POSTing to the webhook URL.
        
        Args:
            framework_input: Payload to send to n8n
            params: Original A2A parameters (for context)
            
        Returns:
            JSON response from n8n webhook
            
        Raises:
            httpx.HTTPError: If the HTTP request fails
        """
        client = await self._get_client()

        headers = {
            "Content-Type": "application/json",
            **self.headers,
        }

        response = await client.post(
            self.webhook_url,
            json=framework_input,
            headers=headers,
        )
        response.raise_for_status()

        return response.json()

    async def from_framework(
        self, framework_output: Dict[str, Any], params: MessageSendParams
    ) -> Message | Task:
        """
        Convert n8n webhook response to A2A Message.
        
        Args:
            framework_output: JSON response from n8n
            params: Original A2A parameters
            
        Returns:
            A2A Message with the n8n response
        """
        # Extract response text from n8n output
        # Support common n8n response formats
        if "output" in framework_output:
            response_text = str(framework_output["output"])
        elif "result" in framework_output:
            response_text = str(framework_output["result"])
        elif "message" in framework_output:
            response_text = str(framework_output["message"])
        else:
            # Fallback: serialize entire response as JSON
            response_text = json.dumps(framework_output, indent=2)

        return Message(
            role="assistant",
            content=[TextPart(type="text", text=response_text)],
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def supports_streaming(self) -> bool:
        """Check if this adapter supports streaming responses."""
        return False

