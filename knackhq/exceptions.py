"""
KnackHQ Exceptions
"""


class ApiResponseError(ValueError):
    """
    KnackHQ API Response Error.
    """

    pass


class NotFoundError(KeyError):
    """
    Generic NotFound API error.
    """

    pass


class ObjectNotFoundError(NotFoundError):
    """
    Could not find KnackHQ Object.
    """

    pass


class RecordNotFoundError(NotFoundError):
    """
    Could not find KnackHQ Record.
    """

    pass
