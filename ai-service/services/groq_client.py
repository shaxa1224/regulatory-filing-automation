from __future__ import annotations

import os
from typing import Any

import requests


class GroqClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.groq.com/openai/v1",
        default_model: str | None = None,
        timeout_s: float = 30.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._default_model = default_model
        self._timeout_s = float(timeout_s)
        self._session = requests.Session()

    @staticmethod
    def from_env() -> "GroqClient":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set.")
        base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()
        default_model = os.getenv("GROQ_MODEL", "").strip() or "llama-3.1-8b-instant"
        timeout_s = float(os.getenv("GROQ_TIMEOUT_S", "30"))
        return GroqClient(
            api_key=api_key,
            base_url=base_url,
            default_model=default_model,
            timeout_s=timeout_s,
        )

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
        top_p: float = 1.0,
        max_tokens: int = 512,
        extra: dict[str, Any] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        resolved_model = (model or self._default_model or "").strip()
        if not resolved_model:
            raise ValueError(
                "Groq model is not set. Provide `model` in the request or set GROQ_MODEL."
            )

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": resolved_model,
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_tokens": int(max_tokens),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if extra:
            payload.update(extra)

        resp = self._session.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=self._timeout_s,
        )
        raw: dict[str, Any]
        try:
            raw = resp.json()
        except Exception:
            raw = {"status_code": resp.status_code, "text": resp.text}

        if resp.status_code >= 400:
            raise ValueError(f"Groq API error ({resp.status_code}): {raw}")

        content = (
            raw.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return str(content), raw

    def list_models(self) -> list[dict[str, Any]]:
        url = f"{self._base_url}/models"
        resp = self._session.get(
            url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=self._timeout_s,
        )
        raw: dict[str, Any]
        try:
            raw = resp.json()
        except Exception:
            raw = {"status_code": resp.status_code, "text": resp.text}

        if resp.status_code >= 400:
            raise ValueError(f"Groq API error ({resp.status_code}): {raw}")

        data = raw.get("data", [])
        if not isinstance(data, list):
            return []
        return [m for m in data if isinstance(m, dict)]
