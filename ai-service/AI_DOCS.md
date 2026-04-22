# AI Service (Flask)

## Endpoints

### `GET /health`
Returns `{ "status": "ok" }`.

### `GET /models`
Lists available Groq models for your API key.

### `POST /categorise`
Request JSON:
- `text` (string, required)
- `model` (string, optional; otherwise `GROQ_MODEL`)
- `temperature` (number, optional)
- `top_p` (number, optional)
- `max_tokens` (int, optional)
- `system_prompt` (string, optional)

Response JSON:
- `cached` (bool)
- `content` (string) – model output (prompt asks for JSON)
- `raw` (object) – raw Groq response (debug)

### `POST /generate-report`
Request JSON:
- `company` (string, required)
- `filing_type` (string, required)
- `period` (string, required)
- `notes` (string, optional)
- `model`, `temperature`, `top_p`, `max_tokens`, `system_prompt` (optional)

Response JSON:
- `cached` (bool)
- `content` (string)
- `raw` (object)

## Caching

In-memory TTL cache:
- `AI_CACHE_TTL_S` (default `600`)
- `AI_CACHE_MAX_ENTRIES` (default `1024`)

Cache key includes prompt + model params, so prompt tuning naturally creates separate cache entries.

## Groq configuration

Environment variables:
- `GROQ_API_KEY` (required)
- `GROQ_MODEL` (required unless `model` passed in request)
- `GROQ_BASE_URL` (default `https://api.groq.com/openai/v1`)
- `GROQ_TIMEOUT_S` (default `30`)

## Run locally

From `ai-service/`:
- `python app.py`
- Or create `ai-service/.env` (see `ai-service/.env.example`) and run `python app.py`

Or with gunicorn:
- `gunicorn -b 0.0.0.0:5000 --factory app:create_app`
