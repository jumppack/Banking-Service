import uuid
from fastapi import Request

def get_request_id(request: Request) -> str:
    """Retrieve the generated or provided request ID from the request state."""
    return getattr(request.state, "request_id", "")

def new_error_id() -> str:
    """Generate a unique identifier for correlating server errors."""
    return uuid.uuid4().hex
