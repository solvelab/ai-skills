class ResponseCodes:
    """Flat registry of response codes. Register a code here before a handler returns it."""

    # generic
    ERROR = "ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # items
    ITEMS_LISTED = "ITEMS_LISTED"
    ITEM_FOUND = "ITEM_FOUND"
    ITEM_CREATED = "ITEM_CREATED"
