"""LLM provider wrapper for architecture extraction."""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_llm_fn():
    """Create an LLM callable based on configuration.

    Returns:
        Callable[[str, str], str] or None if LLM is not configured.
    """
    if not settings.llm_enabled:
        return None

    provider = settings.LLM_PROVIDER.lower()
    api_key = settings.LLM_API_KEY
    model = settings.LLM_MODEL

    if provider == "openai":
        return _openai_fn(api_key, model)
    elif provider == "anthropic":
        return _anthropic_fn(api_key, model)
    elif provider == "openrouter":
        return _openrouter_fn(api_key, model)
    else:
        logger.warning("Unknown LLM provider: %s", provider)
        return None


def _openai_fn(api_key: str, model: str):
    """Return an OpenAI callable."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package not installed")
        return None

    client = OpenAI(api_key=api_key)

    def fn(system_prompt: str, user_prompt: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""

    return fn


def _openrouter_fn(api_key: str, model: str):
    """Return an OpenRouter callable (OpenAI-compatible API)."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package not installed")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    def fn(system_prompt: str, user_prompt: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""

    return fn


def _anthropic_fn(api_key: str, model: str):
    """Return an Anthropic callable."""
    try:
        import anthropic
    except ImportError:
        logger.warning("anthropic package not installed")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    def fn(system_prompt: str, user_prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        for block in response.content:
            if hasattr(block, "text"):
                return block.text  # type: ignore[union-attr]
        return ""

    return fn
