"""A module using export, for validation."""

from pydecor.decorators import export


@export
def exported():
    """Allow testing of @export."""
