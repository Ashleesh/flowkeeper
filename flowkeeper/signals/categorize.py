"""Map a process name to an activity category using the config's app lists."""
from __future__ import annotations

from typing import Dict, List


def categorize_process(process: str, categories: Dict[str, List[str]]) -> str:
    p = (process or "").lower().replace(".exe", "")
    for cat in ("productive", "communication", "browsing"):
        for needle in categories.get(cat, []):
            if needle.lower() in p:
                return cat
    return "other"
