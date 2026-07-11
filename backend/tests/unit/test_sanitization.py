from app.core.sanitization import sanitize_text


def test_sanitize_text_removes_script_and_escapes_html() -> None:
    raw = "<script>alert('x')</script><b>safe</b>"
    out = sanitize_text(raw)
    assert "script" not in out.lower()
    assert "&lt;b&gt;safe&lt;/b&gt;" in out
