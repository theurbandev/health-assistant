TESTING AUTOMATION

# Health Assistant

AI-assisted personal health tracking and insights.

## Project status

Pilot repo for the Garmin API -> home server -> Telegram health assistant.

## Design

- FastAPI runs on the home server.
- Garmin remains the source of truth.
- A local SQLite cache stores synchronized Garmin responses for fast historical questions.
- The model receives the `garmin-health` skill and can request read-only Garmin data endpoints as needed.
- Telegram is the only supported chat channel in the first version.

The runtime does **not** start a Codex session for each Telegram message. It calls the configured model API directly.

## Local setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload
```

The original stdlib test suite can be run with:

```bash
python3 -m unittest discover -s tests -q
```

Health check: http://localhost:8000/healthz

No real Garmin or model requests are made until the corresponding credentials are configured.

## Secrets

`.env` is intentionally ignored by Git. Never commit Garmin credentials, Telegram tokens, model API keys,
encryption keys, database files, or health data.

## Current implementation boundary

The Garmin adapter and endpoint catalog are deliberately interfaces until the Garmin developer application is
approved and its exact API contracts are available. Mock data can be used to test the agent loop before then.
