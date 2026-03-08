"""
llm_client.py
Wraps OpenAI-compatible API calls (supports DeepSeek / OpenAI / any compatible endpoint).
Uses explicit httpx client to avoid the 'proxies' argument conflict in older openai SDK versions.
"""

import json
import openai

try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False


class LLMClient:
    def __init__(self, config_path: str = "config/llm_config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.model_name = config["model_name"]
        base_url = config.get("base_url", "https://api.openai.com/v1")
        api_key  = config["api_key"]

        if _HTTPX_AVAILABLE:
            http_client = httpx.Client()
            self._client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url,
                http_client=http_client,
            )
        else:
            self._client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url,
            )

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=temperature,
            timeout=120,
        )
        return response.choices[0].message.content.strip()