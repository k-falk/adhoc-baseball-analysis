"""Shared helpers: resilient HTTP with retries."""
from __future__ import annotations
import time
import requests
from io import StringIO
import pandas as pd

DEFAULT_HEADERS = {
    "User-Agent": "adhoc-baseball-analysis/1.0 (research; claude-code)"
}


def get_json(url: str, params: dict | None = None, *, retries: int = 5, timeout: int = 60):
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers=DEFAULT_HEADERS)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/json"):
                return r.json()
            if r.status_code == 200:
                # some endpoints return JSON without content-type
                try:
                    return r.json()
                except Exception:
                    pass
            last = f"status={r.status_code} body={r.text[:120]!r}"
        except Exception as e:
            last = str(e)
        time.sleep(2 ** i)
    raise RuntimeError(f"get_json failed for {url}: {last}")


def get_csv(url: str, *, retries: int = 5, timeout: int = 120) -> pd.DataFrame:
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)
            if r.status_code == 200 and r.text.strip():
                return pd.read_csv(StringIO(r.text))
            last = f"status={r.status_code} body={r.text[:120]!r}"
        except Exception as e:
            last = str(e)
        time.sleep(2 ** i)
    raise RuntimeError(f"get_csv failed for {url}: {last}")
