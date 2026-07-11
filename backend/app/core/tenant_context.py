import contextvars
import uuid

_request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
_tenant_id_ctx: contextvars.ContextVar[uuid.UUID | None] = contextvars.ContextVar("tenant_id", default=None)


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def get_request_id() -> str | None:
    return _request_id_ctx.get()


def set_tenant_id(tenant_id: uuid.UUID | None) -> None:
    _tenant_id_ctx.set(tenant_id)


def get_tenant_id() -> uuid.UUID | None:
    return _tenant_id_ctx.get()
