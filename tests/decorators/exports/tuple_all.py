"""A module using export, for validation."""

__all__ = ("first",)

from pydecor.decorators import export


def first():
    """Allow testing of __all__ appending."""


@export
def exported():
    """Allow testing of @export."""
