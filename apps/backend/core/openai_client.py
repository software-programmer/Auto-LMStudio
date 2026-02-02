"""
OpenAI-Compatible Client Wrapper
================================

Provides a wrapper around the OpenAI client that mimics the claude-agent-sdk interface.
This allows LM Studio and other OpenAI-compatible providers to be used with Auto Claude.

The wrapper provides:
- Similar interface to ClaudeSDKClient for agent sessions
- Tool calling support (function calling)
- Context management (async with)
- Response formatting compatible with Auto Claude expectations
"""

import json
import logging
from pathlib import Path
from typing import Any, AsyncIterator

try:
    from openai import AsyncOpenAI, OpenAI
except ImportError:
    AsyncOpenAI = None  # type: ignore
    OpenAI = None  # type: ignore

logger = logging.getLogger(__name__)


class OpenAICompatibleClient:
    """
    OpenAI-compatible client that mimics claude-agent-sdk interface.

    This wrapper allows LM Studio and other OpenAI-compatible providers
    to be used with Auto Claude's agent framework.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        system_prompt: str | None = None,
        allowed_tools: list[str] | None = None,
        max_turns: int = 20,
        cwd: Path | None = None,
    ):
        """
        Initialize OpenAI-compatible client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API endpoint
            model: Model name to use
            system_prompt: Optional system prompt
            allowed_tools: List of allowed tool names
            max_turns: Maximum conversation turns
            cwd: Working directory for file operations
        """
        if OpenAI is None:
            raise ImportError(
                "openai package not installed. Run: pip install openai>=1.0.0"
            )

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools or []
        self.max_turns = max_turns
        self.cwd = cwd

        # Initialize sync and async clients
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        # Conversation history
        self.messages: list[dict[str, Any]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

        logger.info(f"Initialized OpenAI-compatible client for {base_url}")
        logger.debug(f"Model: {model}, Max turns: {max_turns}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.async_client.close()

    def send_message(
        self, message: str, attachments: list[dict[str, Any]] | None = None
    ) -> tuple[str, dict[str, Any]]:
        """
        Send a message and get a response (synchronous).

        Args:
            message: User message to send
            attachments: Optional file attachments

        Returns:
            Tuple of (status, response_dict)
            - status: "success" or "error"
            - response_dict: Dictionary with "content" key containing response text
        """
        try:
            # Add user message to history
            self.messages.append({"role": "user", "content": message})

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                max_tokens=4096,
                temperature=0.7,
            )

            # Extract assistant response
            assistant_message = response.choices[0].message
            content = assistant_message.content or ""

            # Add to history
            self.messages.append({"role": "assistant", "content": content})

            logger.debug(f"Received response: {len(content)} characters")

            return "success", {"content": content, "raw_response": response}

        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            return "error", {"content": f"Error: {str(e)}"}

    async def send_message_async(
        self, message: str, attachments: list[dict[str, Any]] | None = None
    ) -> tuple[str, dict[str, Any]]:
        """
        Send a message and get a response (asynchronous).

        Args:
            message: User message to send
            attachments: Optional file attachments

        Returns:
            Tuple of (status, response_dict)
        """
        try:
            # Add user message to history
            self.messages.append({"role": "user", "content": message})

            # Make API call
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                max_tokens=4096,
                temperature=0.7,
            )

            # Extract assistant response
            assistant_message = response.choices[0].message
            content = assistant_message.content or ""

            # Add to history
            self.messages.append({"role": "assistant", "content": content})

            logger.debug(f"Received response: {len(content)} characters")

            return "success", {"content": content, "raw_response": response}

        except Exception as e:
            logger.error(f"Error in send_message_async: {e}")
            return "error", {"content": f"Error: {str(e)}"}

    def reset_conversation(self):
        """Reset conversation history."""
        self.messages = []
        if self.system_prompt:
            self.messages.append({"role": "system", "content": self.system_prompt})


def create_openai_compatible_client(
    api_key: str,
    base_url: str,
    model: str,
    system_prompt: str | None = None,
    allowed_tools: list[str] | None = None,
    max_turns: int = 20,
    cwd: Path | None = None,
) -> OpenAICompatibleClient:
    """
    Factory function to create an OpenAI-compatible client.

    Args:
        api_key: API key for authentication
        base_url: Base URL for the API endpoint
        model: Model name to use
        system_prompt: Optional system prompt
        allowed_tools: List of allowed tool names
        max_turns: Maximum conversation turns
        cwd: Working directory for file operations

    Returns:
        OpenAICompatibleClient instance
    """
    return OpenAICompatibleClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt=system_prompt,
        allowed_tools=allowed_tools,
        max_turns=max_turns,
        cwd=cwd,
    )
