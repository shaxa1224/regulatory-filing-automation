import json
import os
from datetime import datetime, timezone

import requests


def main() -> int:
    base_url = os.getenv("AI_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "demo")
    )
    os.makedirs(out_dir, exist_ok=True)

    results = {
        "base_url": base_url,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "health": None,
        "models": None,
        "categorise_1": None,
        "categorise_2": None,
        "generate_report": None,
    }

    def req(method: str, path: str, json_body=None, timeout=180):
        url = f"{base_url}{path}"
        r = requests.request(method, url, json=json_body, timeout=timeout)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return {"status_code": r.status_code, "body": body}

    results["health"] = req("GET", "/health", timeout=30)
    results["models"] = req("GET", "/models", timeout=60)

    categorise_body = {"text": "Need to file 10-K for FY2025", "max_tokens": 120}
    results["categorise_1"] = req("POST", "/categorise", json_body=categorise_body, timeout=180)
    results["categorise_2"] = req("POST", "/categorise", json_body=categorise_body, timeout=180)

    report_body = {
        "company": "Acme Inc",
        "filing_type": "10-K",
        "period": "FY2025",
        "notes": "Use placeholders for missing financials.",
        "max_tokens": 350,
    }
    results["generate_report"] = req(
        "POST", "/generate-report", json_body=report_body, timeout=300
    )

    json_path = os.path.join(out_dir, "demo_output.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    text_path = os.path.join(out_dir, "demo_output.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(results, ensure_ascii=False, indent=2))
        f.write("\n")

    html_path = os.path.join(out_dir, "demo_output.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(
            "<!doctype html>\n"
            "<html lang='en'>\n"
            "<head>\n"
            "  <meta charset='utf-8'/>\n"
            "  <meta name='viewport' content='width=device-width, initial-scale=1'/>\n"
            "  <title>AI Service Demo Output</title>\n"
            "  <style>\n"
            "    body{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"
            "         margin:24px; color:#111;}\n"
            "    h1{font-size:18px; margin:0 0 12px 0;}\n"
            "    .meta{font-size:12px; color:#444; margin-bottom:12px;}\n"
            "    pre{white-space:pre-wrap; word-break:break-word; padding:14px; border:1px solid #ddd; border-radius:10px;"
            "        background:#fafafa; font-size:12px; line-height:1.35;}\n"
            "  </style>\n"
            "</head>\n"
            "<body>\n"
            "  <h1>AI Service Demo Output</h1>\n"
            f"  <div class='meta'>Base URL: {base_url} | Captured (UTC): {results['captured_at_utc']}</div>\n"
            "  <pre id='out'></pre>\n"
            "  <script>\n"
            "    const data = "
            + json.dumps(results, ensure_ascii=False)
            + ";\n"
            "    document.getElementById('out').textContent = JSON.stringify(data, null, 2);\n"
            "  </script>\n"
            "</body>\n"
            "</html>\n"
        )

    print(json_path)
    print(html_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

