from typing import List


class APIException(Exception):
    """
    Raise this inside routes or services to return structured errors.
    """
    def __init__(self, status_code: int, message: str, errors: List[str] | None = None):
        self.status_code = status_code
        self.message = message
        self.errors = errors or []
        super().__init__(message)
