"""Check Kimi Coding quota without printing credential or account identifiers."""

from __future__ import annotations

import json
import pathlib
import sys
import urllib.request
from datetime import datetime, timezone

import yaml


config = yaml.safe_load((pathlib.Path.home() / ".bub" / "config.yml").read_text())
api_keys = config["api_key"]
key = api_keys["anthropic"] if isinstance(api_keys, dict) else api_keys
request = urllib.request.Request(
    "https://api.kimi.com/coding/v1/usages",
    headers={"Authorization": f"Bearer {key}"},
)
response = json.loads(urllib.request.urlopen(request, timeout=20).read())
weekly = response.get("usage") or {}
five_hour = next(
    (
        item.get("detail") or {}
        for item in response.get("limits") or []
        if (item.get("window") or {}).get("duration") == 300
    ),
    {},
)


def used(detail: dict):
    value = detail.get("used")
    if value is not None:
        return value
    try:
        return str(int(detail["limit"]) - int(detail["remaining"]))
    except (KeyError, TypeError, ValueError):
        return None


def available(detail: dict) -> bool:
    try:
        return int(used(detail)) < int(detail["limit"])
    except (KeyError, TypeError, ValueError):
        return False


result = {
    "checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "available": available(weekly) and available(five_hour),
    "five_hour": {
        "used": used(five_hour),
        "limit": five_hour.get("limit"),
        "reset_time": five_hour.get("resetTime"),
    },
    "weekly": {
        "used": used(weekly),
        "limit": weekly.get("limit"),
        "remaining": weekly.get("remaining"),
        "reset_time": weekly.get("resetTime"),
    },
    "parallel_limit": (response.get("parallel") or {}).get("limit"),
}
print(json.dumps(result, separators=(",", ":")), flush=True)
sys.exit(0 if result["available"] else 1)
