from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, jsonify, request

from services.cache import ResponseCache
from services.groq_client import GroqClient
from services.prompt_store import PromptStore

from ._shared import require_json, stable_key

bp = Blueprint("generate_report", __name__)

_cache = ResponseCache(
    ttl_s=int(os.getenv("AI_CACHE_TTL_S", "600")),
    max_entries=int(os.getenv("AI_CACHE_MAX_ENTRIES", "1024")),
)
_prompts = PromptStore.from_default_location()


def _get_client() -> GroqClient:
    return GroqClient.from_env()


@bp.post("/generate-report")
def generate_report():
    try:
        payload = require_json(request)

        company = (payload.get("company") or "").strip()
        filing_type = (payload.get("filing_type") or "").strip()
        period = (payload.get("period") or "").strip()
        notes = (payload.get("notes") or "").strip()

        if not company or not filing_type or not period:
            return (
                jsonify(
                    {
                        "error": "Missing required fields: company, filing_type, period",
                    }
                ),
                400,
            )

        model = payload.get("model")
        temperature = payload.get("temperature", 0.3)
        top_p = payload.get("top_p", 1.0)
        max_tokens = payload.get("max_tokens", 1200)

        system_prompt = payload.get(
            "system_prompt",
            "You generate clear, compliance-friendly drafts. "
            "Do not invent facts; if data is missing, add TODO placeholders.",
        )
        user_prompt = _prompts.render(
            "generate_report.txt",
            company=company,
            filing_type=filing_type,
            period=period,
            notes=notes,
        )

        cache_key = stable_key(
            "generate-report",
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
