"""
LLM Provider Abstraction Layer
==============================

Provides a unified interface for multiple LLM providers:
- Claude (via claude-agent-sdk) - OAuth authentication
- LM Studio (via OpenAI-compatible API) - API key authentication
- OpenAI (via OpenAI API) - API key authentication

This allows Auto Claude to work with different model providers while maintaining
a consistent interface throughout the codebase.
"""

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    CLAUDE = "claude"
    LM_STUDIO = "lm_studio"
    OPENAI = "openai"


def get_active_provider() -> LLMProvider:
    """
    Determine the active LLM provider based on environment variables.

    Priority:
    1. LLM_PROVIDER environment variable (explicit override)
    2. Default to CLAUDE

    Returns:
        Active LLM provider enum value
    """
    # Explicit provider override
    provider_env = os.environ.get("LLM_PROVIDER", "").lower()
    if provider_env == "lm_studio":
        logger.info("LLM_PROVIDER set to lm_studio")
        return LLMProvider.LM_STUDIO
    elif provider_env == "openai":
        logger.info("LLM_PROVIDER set to openai")
        return LLMProvider.OPENAI
    elif provider_env == "claude":
        logger.info("LLM_PROVIDER set to claude")
        return LLMProvider.CLAUDE

    # Default to Claude unless explicitly set
    # This ensures backward compatibility - existing users won't be affected
    logger.debug("Using default Claude provider")
    return LLMProvider.CLAUDE


def get_provider_config() -> dict[str, Any]:
    """
    Get configuration for the active LLM provider.

    Returns:
        Dictionary with provider-specific configuration:
        - provider: LLMProvider enum
        - base_url: API endpoint URL
        - api_key: API key or auth token
        - default_model: Default model name
        - supports_thinking: Whether provider supports extended thinking
        - supports_tools: Whether provider supports function calling
    """
    provider = get_active_provider()

    if provider == LLMProvider.LM_STUDIO:
        base_url = os.environ.get(
            "ANTHROPIC_BASE_URL", "http://192.168.1.85:1234/v1"
        )
        # Ensure base_url ends with /v1
        if not base_url.endswith("/v1"):
            base_url = base_url.rstrip("/") + "/v1"

        return {
            "provider": provider,
            "base_url": base_url,
            "api_key": os.environ.get("ANTHROPIC_AUTH_TOKEN", "lm-studio"),
            "default_model": os.environ.get("ANTHROPIC_MODEL", "local-model"),
            "supports_thinking": False,  # LM Studio doesn't support Claude's extended thinking
            "supports_tools": True,  # Most LM Studio models support function calling
        }

    elif provider == LLMProvider.OPENAI:
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.openai.com/v1")
        return {
            "provider": provider,
            "base_url": base_url,
            "api_key": os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or os.environ.get("OPENAI_API_KEY", ""),
            "default_model": os.environ.get("ANTHROPIC_MODEL", "gpt-4"),
            "supports_thinking": False,  # OpenAI doesn't have Claude's extended thinking
            "supports_tools": True,  # OpenAI supports function calling
        }

    else:  # CLAUDE
        return {
            "provider": provider,
            "base_url": os.environ.get(
                "ANTHROPIC_BASE_URL", "https://api.anthropic.com"
            ),
            "api_key": None,  # Claude uses OAuth, handled by claude-agent-sdk
            "default_model": os.environ.get(
                "ANTHROPIC_MODEL", "claude-opus-4-5-20251101"
            ),
            "supports_thinking": True,  # Claude supports extended thinking
            "supports_tools": True,  # Claude supports function calling
        }


def should_use_claude_sdk() -> bool:
    """
    Determine if we should use claude-agent-sdk or fall back to OpenAI-compatible client.

    Returns:
        True if Claude SDK should be used, False otherwise
    """
    provider = get_active_provider()
    return provider == LLMProvider.CLAUDE


def get_openai_compatible_config() -> dict[str, Any]:
    """
    Get OpenAI-compatible client configuration for non-Claude providers.

    Returns:
        Dictionary with OpenAI client configuration
    """
    config = get_provider_config()

    return {
        "api_key": config["api_key"],
        "base_url": config["base_url"],
        "default_model": config["default_model"],
    }
