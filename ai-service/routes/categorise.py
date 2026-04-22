from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, jsonify, request

from services.cache import ResponseCache
from services.groq_client import GroqClient
from services.prompt_store import PromptStore

from ._shared import require_json, stable_key

bp = Blueprint("categorise", __name__)

_cache = ResponseCache(
    ttl_s=int(os.getenv("AI_CACHE_TTL_S", "600")),
    max_entries=int(os.getenv("AI_CACHE_MAX_ENTRIES", "1024")),
)
_prompts = PromptStore.from_default_location()


def _get_client() -> GroqClient:
    return GroqClient.from_env()


@bp.post("/categorise")
def categorise():
    try:
        payload = require_json(request)
        text = (payload.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Missing required field: text"}), 400

        model = payload.get("model")
        temperature = payload.get("temperature", 0.2)
        top_p = payload.get("top_p", 1.0)
        max_tokens = payload.get("max_tokens", 256)

        system_prompt = payload.get(
            "system_prompt",
            "You are a precise assistant for regulatory filing automation. "
            "Return concise, structured JSON only.",
        )
        user_prompt = _prompts.render("categorise.txt", text=text)

        cache_key = stable_key(
            "categorise",
            {
                "model": model,
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            },
        )

        cached = _cache.get(cache_key)
        if cached is not None:
            return jsonify({"cached": True, **cached})

        client = _get_client()
        content, raw = client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=float(temperature),
            top_p=float(top_p),
            max_tokens=int(max_tokens),
        )

        result: dict[str, Any] = {"content": content, "raw": raw}
        _cache.set(cache_key, result)
        return jsonify({"cached": False, **result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500
