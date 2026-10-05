# Verification Report

## API fallback
- Real API is attempted first.
- Connection/timeout/HTTP/invalid-response failures trigger Mock API fallback.
- Remote Mock API is used when `mock_api_url` is configured.
- Bundled local Mock API data is used when the remote Mock API is unavailable.
- Added automated unit test that simulates a real API connection failure and verifies Mock fallback.

## Files changed
- `app/sources/api_source.py`
- `main.py`
- `config.json`
- `data/mock/api_students.json`
- `tests/test_pipeline.py`
- `README.md`

## Verification
Run:

```bash
python -m unittest discover -s tests -v
```

The full live pipeline also requires PostgreSQL and MongoDB services to be running and configured locally.

## Result
Automated unit tests: **9 tests run, 8 passed, 1 skipped**. The skipped test requires a live PostgreSQL/MongoDB environment.
Python syntax compilation: **passed**.
