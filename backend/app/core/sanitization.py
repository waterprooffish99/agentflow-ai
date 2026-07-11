import html
import re

_SCRIPT_RE = re.compile(r"<\s*script[^>]*>(.*?)<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)


def sanitize_text(value: str) -> str:
    trimmed = value.strip()
    without_scripts = _SCRIPT_RE.sub("", trimmed)
    return html.escape(without_scripts)
