from __future__ import annotations

from flask import Blueprint, jsonify

from services.groq_client import GroqClient

bp = Blueprint("models", __name__)


@bp.get("/models")
def models():
    try:
        client = GroqClient.from_env()
        models = client.list_models()
        # Keep response small + easy to scan
        ids = [m.get("id") for m in models if m.get("id")]
        return jsonify({"models": ids, "count": len(ids)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500

