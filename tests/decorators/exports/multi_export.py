"""All varieties of acceptable exports."""

from pydecor.decorators import export


@export
class Exported:
    def foo(self):
        pass


@export
def exported():
    pass
