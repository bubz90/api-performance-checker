import json
import os
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


_ALLOWED_SCHEMES = {"http", "https"}


def _validate_url(url):
    """Return an error string if the URL is invalid, else None."""
    try:
        parsed = urlparse(url)
    except Exception:
        return "Invalid URL"
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return f"URL scheme must be http or https (got '{parsed.scheme}')"
    if not parsed.netloc:
        return "URL must include a host"
    return None


def make_request(url, method, headers, body):
    start = time.perf_counter()
    error = None
    status_code = None
    response_body = None
    response_headers = {}
    try:
        resp = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=body if body else None,
            timeout=30,
            allow_redirects=True,
        )
        status_code = resp.status_code
        response_headers = dict(resp.headers)
        try:
            response_body = resp.json()
        except Exception:
            response_body = resp.text
    except Exception as exc:
        error = str(exc)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return {
        "status_code": status_code,
        "elapsed_ms": elapsed_ms,
        "response_body": response_body,
        "response_headers": response_headers,
        "error": error,
    }


@app.route("/")
def index():
    history = load_history()
    last = history[-1] if history else None
    return render_template("index.html", last_execution=last)


@app.route("/history")
def get_history():
    history = load_history()
    return jsonify(history)


@app.route("/history/clear", methods=["POST"])
def clear_history():
    save_history([])
    return jsonify({"ok": True})


@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    method = (data.get("method") or "GET").strip().upper()
    auth_header = (data.get("auth_header") or "").strip()
    extra_headers_raw = (data.get("headers") or "").strip()
    body = (data.get("body") or "").strip()
    count = max(1, int(data.get("count") or 1))

    if not url:
        return jsonify({"error": "URL is required"}), 400

    url_error = _validate_url(url)
    if url_error:
        return jsonify({"error": url_error}), 400

    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header
    if extra_headers_raw:
        try:
            parsed = json.loads(extra_headers_raw)
            if isinstance(parsed, dict):
                headers.update(parsed)
        except json.JSONDecodeError:
            return jsonify({"error": "Headers must be valid JSON object"}), 400

    results = []
    for i in range(count):
        result = make_request(url, method, headers, body)
        result["index"] = i + 1
        results.append(result)

    history = load_history()
    entry = {
        "id": len(history) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "method": method,
        "auth_header": auth_header,
        "headers": extra_headers_raw,
        "body": body,
        "count": count,
        "results": results,
        "avg_ms": round(
            sum(r["elapsed_ms"] for r in results) / len(results), 2
        ),
        "min_ms": min(r["elapsed_ms"] for r in results),
        "max_ms": max(r["elapsed_ms"] for r in results),
    }
    history.append(entry)
    save_history(history)

    return jsonify(entry)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=5000)
