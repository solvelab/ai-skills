from typing import Any


def success(code: str, message: str, data: Any = None) -> dict:
    """The success envelope every endpoint returns. `data` is omitted when None."""
    body: dict[str, Any] = {"status": "success", "code": code, "message": message}
    if data is not None:
        body["data"] = data
    return body
