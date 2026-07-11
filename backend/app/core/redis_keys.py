import uuid


def tenant_key(tenant_id: uuid.UUID | str, *parts: str) -> str:
    t = str(tenant_id)
    joined = ":".join(parts)
    return f"tenant:{t}:{joined}"
