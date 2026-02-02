"""
Simple Claude SDK Client Factory
================================

Factory for creating minimal Claude SDK clients for single-turn utility operations
like commit message generation, merge conflict resolution, and batch analysis.

These clients don't need full security configurations, MCP servers, or hooks.
Use `create_client()` from `core.client` for full agent sessions with security.

Example usage:
    from core.simple_client import create_simple_client

    # For commit message generation (text-only, no tools)
    client = create_simple_client(agent_type="commit_message")

    # For merge conflict resolution (text-only, no tools)
    client = create_simple_client(agent_type="merge_resolver")

    # For insights extraction (read tools only)
    client = create_simple_client(agent_type="insights", cwd=project_dir)
"""

import logging
import os
from pathlib import Path

from agents.tools_pkg import get_agent_config, get_default_thinking_level
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from core.auth import (
    configure_sdk_authentication,
    get_sdk_env_vars,
)
from core.llm_provider import (
    get_openai_compatible_config,
    should_use_claude_sdk,
    get_active_provider,
)
from core.openai_client import create_openai_compatible_client
from core.platform import validate_cli_path
from phase_config import get_thinking_budget

logger = logging.getLogger(__name__)


def create_simple_client(
    agent_type: str = "merge_resolver",
    model: str = "claude-haiku-4-5-20251001",
    system_prompt: str | None = None,
    cwd: Path | None = None,
    max_turns: int = 1,
    max_thinking_tokens: int | None = None,
) -> ClaudeSDKClient:
    """
    Create a minimal Claude SDK client for single-turn utility operations.

    This factory creates lightweight clients without MCP servers, security hooks,
    or full permission configurations. Use for text-only analysis tasks.

    Args:
        agent_type: Agent type from AGENT_CONFIGS. Determines available tools.
                   Common utility types:
                   - "merge_resolver" - Text-only merge conflict analysis
                   - "commit_message" - Text-only commit message generation
                   - "insights" - Read-only code insight extraction
                   - "batch_analysis" - Read-only batch issue analysis
                   - "batch_validation" - Read-only validation
        model: Claude model to use (defaults to Haiku for fast/cheap operations)
        system_prompt: Optional custom system prompt (for specialized tasks)
        cwd: Working directory for file operations (optional)
        max_turns: Maximum conversation turns (default: 1 for single-turn)
        max_thinking_tokens: Override thinking budget (None = use agent default from
                            AGENT_CONFIGS, converted using phase_config.THINKING_BUDGET_MAP)

    Returns:
        Configured ClaudeSDKClient for single-turn operations

    Raises:
        ValueError: If agent_type is not found in AGENT_CONFIGS
    """
    # Get environment variables for SDK (including CLAUDE_CONFIG_DIR if set)
    sdk_env = get_sdk_env_vars()

    # Get the config dir for profile-specific credential lookup
    # CLAUDE_CONFIG_DIR enables per-profile Keychain entries with SHA256-hashed service names
    config_dir = sdk_env.get("CLAUDE_CONFIG_DIR")

    # Configure SDK authentication (OAuth or API profile mode)
    configure_sdk_authentication(config_dir)

    # Get agent configuration (raises ValueError if unknown type)
    config = get_agent_config(agent_type)

    # Get tools from config (no MCP tools for simple clients)
    allowed_tools = list(config.get("tools", []))

    # Determine thinking budget using the single source of truth (phase_config.py)
    if max_thinking_tokens is None:
        thinking_level = get_default_thinking_level(agent_type)
        max_thinking_tokens = get_thinking_budget(thinking_level)

    # Build options dict
    # Note: SDK bundles its own CLI, so no cli_path detection needed
    options_kwargs = {
        "model": model,
        "system_prompt": system_prompt,
        "allowed_tools": allowed_tools,
        "max_turns": max_turns,
        "cwd": str(cwd.resolve()) if cwd else None,
        "env": sdk_env,
    }

    # Only add max_thinking_tokens if not None (Haiku doesn't support extended thinking)
    if max_thinking_tokens is not None:
        options_kwargs["max_thinking_tokens"] = max_thinking_tokens

    # Optional: Allow CLI path override via environment variable
    env_cli_path = os.environ.get("CLAUDE_CLI_PATH")
    if env_cli_path and validate_cli_path(env_cli_path):
        options_kwargs["cli_path"] = env_cli_path
        logger.info(f"Using CLAUDE_CLI_PATH override: {env_cli_path}")

    # Route to appropriate client based on provider
    if should_use_claude_sdk():
        # Use Claude Agent SDK for Claude provider
        return ClaudeSDKClient(options=ClaudeAgentOptions(**options_kwargs))
    else:
        # Use OpenAI-compatible client for LM Studio and other providers
        provider = get_active_provider()
        logger.info(f"Using {provider.value} provider with OpenAI-compatible client")

        oai_config = get_openai_compatible_config()

        # Create OpenAI-compatible client with similar configuration
        return create_openai_compatible_client(
            api_key=oai_config["api_key"],
            base_url=oai_config["base_url"],
            model=model,  # Use the model passed to this function
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            max_turns=max_turns,
            cwd=cwd,
        )
