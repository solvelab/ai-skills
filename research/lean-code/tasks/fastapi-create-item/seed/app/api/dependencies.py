from fastapi import Header

from app.core.exceptions import UnauthorizedException


def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    """The calling tenant, from the gateway-set header. Never read it from the body."""
    if not x_tenant_id:
        raise UnauthorizedException("Missing X-Tenant-Id header")
    return x_tenant_id
