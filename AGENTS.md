# AGENTS.md

Instructions for AI coding agents working in this repository.

## Stack

- Python 3 (stdlib-first; avoid new dependencies unless necessary)
- Tests: `unittest`, in `tests/` (run: `python3 -m unittest discover -s tests -q`)

## Conventions

- Keep modules small and focused under `health_assistant/`.
- Every new behavior ships with unit tests.
- Follow PEP 8; no external dependencies unless a comment justifies them.
- Do not commit secrets, credentials, or personal health data (real or sample).

## Workflow

- Read the issue's acceptance criteria before starting.
- Make minimal, focused changes; run the full test suite before finishing.
- Report test results in your final summary.
