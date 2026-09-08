import os

from .base import LLMProvider
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider


def build_provider() -> LLMProvider | None:
    provider_name = os.getenv("COPILOT_LLM_PROVIDER", "").strip().lower()
    model = os.getenv("COPILOT_LLM_MODEL", "").strip()

    if not provider_name or not model:
        return None

    if provider_name == "ollama":
        base_url = os.getenv("COPILOT_LLM_BASE_URL", "http://localhost:11434")
        return OllamaProvider(model=model, base_url=base_url)

    if provider_name == "openai":
        api_key = os.getenv("COPILOT_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        base_url = os.getenv(
            "COPILOT_LLM_BASE_URL",
            os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        return OpenAICompatibleProvider(
            model=model,
            base_url=base_url,
            api_key=api_key,
        )

    if provider_name in {"openai-compatible", "openai_compatible"}:
        base_url = os.getenv("COPILOT_LLM_BASE_URL", "").strip()
        if not base_url:
            return None
        api_key = os.getenv("COPILOT_LLM_API_KEY")
        return OpenAICompatibleProvider(
            model=model,
            base_url=base_url,
            api_key=api_key,
        )

    return None
