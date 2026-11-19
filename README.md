# AI Marketing Intelligence Assistant — Backend Starter

This is **Phase 1 only**: FastAPI setup, React development CORS, health endpoints, and tests. It does not yet implement audits, authentication, database access, or Gemini.

## PyCharm setup (Windows)
1. Open this folder in PyCharm.
2. Select a Python 3.11+ interpreter and create a virtual environment if needed.
3. In the PyCharm terminal run `python -m pip install -r requirements.txt`.
4. Start with `python -m uvicorn app.main:app --reload`.
5. Open `http://127.0.0.1:8000/docs` and `http://127.0.0.1:8000/health`.
6. Run `python -m pytest -q`.

The React app can call the two health endpoints. The audit API is not implemented yet.
