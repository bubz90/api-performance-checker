# API Performance Checker

Lightweight Flask app for testing API response time, comparing runs, and tracking performance history in a local UI.

## Features

- Execute one request instantly.
- Run sequential batch requests using Repeat N times.
- Run interval mode using:
	- Repeat N times as total number of executions.
	- Interval (seconds) as delay between each execution.
- Hard stop button to cancel scheduled and in-flight executions.
- Response metrics per run: average, min, max, status, and response preview.
- Local history storage and comparison of selected runs.
- Built-in response-time history chart.

## Requirements

- Python 3.9+
- pip

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
source .venv/bin/activate
python app.py
```

Default URL:

- http://127.0.0.1:5000

If port 5000 is already in use, run with Flask CLI on another port:

```bash
source .venv/bin/activate
FLASK_APP=app.py flask run --host 0.0.0.0 --port 5001
```

## How To Use

1. Choose method and enter target URL.
2. Optional: add Authorization header value.
3. Optional: add extra headers as JSON object.
4. Optional: add request body.
5. Use one of the execution modes:
	 - Execute Once: sends 1 request.
	 - Sequential: sends N requests in one batch.
	 - Interval: sends 1 request every interval, repeated N times.
6. Use Stop to immediately cancel active/scheduled interval execution.
7. Inspect results, history, comparison, and chart.

## Notes

- History is persisted in history.json in the project root.
- URL validation accepts only http and https schemes.
- Extra headers field must be valid JSON object, for example:

```json
{"Content-Type": "application/json", "X-Custom": "value"}
```

## API Endpoints

- GET /
- POST /execute
- GET /history
- POST /history/clear

## Dependencies

- Flask
- Requests
