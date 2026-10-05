import json
from pathlib import Path

import pandas as pd
import requests


def _normalize_payload(payload, student_id_offset=0):
    """Convert a REST API JSON payload to the pipeline's internal schema."""
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        records = payload["data"]
    elif isinstance(payload, list):
        records = payload
    else:
        raise ValueError("API returned an unexpected JSON structure")

    if not records:
        raise ValueError("API returned an empty student collection")

    df = pd.DataFrame(records)
    required = {"id", "name"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"API response is missing required fields: {sorted(missing)}")

    df = df.rename(columns={"id": "student_id", "name": "api_name", "course": "api_course"})
    df["student_id"] = pd.to_numeric(df["student_id"], errors="coerce") + student_id_offset
    if "api_course" not in df.columns:
        df["api_course"] = pd.NA

    return df[["student_id", "api_name", "api_course"]]


def _request_api(url, timeout, logger, student_id_offset=0, source_name="API"):
    logger.info("%s extraction started: %s", source_name, url)
    response = requests.get(
        url,
        timeout=timeout,
        headers={"Accept": "application/json", "User-Agent": "StudentDataPipeline/1.0"},
    )
    response.raise_for_status()
    return _normalize_payload(response.json(), student_id_offset)


def _load_local_mock(mock_data_path, student_id_offset=0):
    """Load the bundled Mock API response when no remote Mock API is configured."""
    path = Path(mock_data_path)
    if not path.exists():
        raise FileNotFoundError(f"Mock API data file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _normalize_payload(payload, student_id_offset)


def extract_api(url, timeout, logger, student_id_offset=0, mock_api_url=None,
                mock_api_timeout=None, mock_data_path=None):
    """
    Try the real API first.

    If the real API cannot be reached or returns an invalid response, automatically
    fall back to Mock API. If mock_api_url is not configured, the bundled local
    Mock API response is used so the pipeline can still run offline.
    """
    try:
        df = _request_api(
            url, timeout, logger, student_id_offset=student_id_offset,
            source_name="Real REST API",
        )
        logger.info("Real REST API succeeded with %s records", len(df))
        return df

    except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
        logger.warning("Real REST API failed: %s. Switching to Mock API.", exc)

    # First preference: remote Mock API, if configured.
    if mock_api_url:
        try:
            df = _request_api(
                mock_api_url,
                mock_api_timeout or timeout,
                logger,
                student_id_offset=student_id_offset,
                source_name="Mock API",
            )
            logger.warning("Mock API fallback succeeded with %s records", len(df))
            return df
        except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
            logger.warning("Mock API URL failed: %s. Trying bundled local Mock API.", exc)

    # Guaranteed educational fallback: local mock response shipped with the project.
    if mock_data_path:
        df = _load_local_mock(mock_data_path, student_id_offset=student_id_offset)
        logger.warning("Bundled local Mock API fallback succeeded with %s records", len(df))
        return df

    raise RuntimeError("Real API failed and no Mock API fallback is configured.")
