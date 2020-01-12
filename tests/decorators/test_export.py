# -*- coding: UTF-8 -*-
"""Tests for the @export decorator."""

import importlib
import sys
import textwrap
import types
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec

import pytest

from pydecor.decorators import export


@pytest.fixture()
def reset_modules():
    """Ensure sys.modules is reset at the end of a test."""
    modules = dict(sys.modules)
    yield
    sys.modules = modules


class TestExport:
    """Test the @export decorator."""

    def test_bad_type(self):
        """Passing something with no __module__ attribute is a TypeError."""
        with pytest.raises(TypeError):
            export("foo")

    def test_not_in_modules(self):
        """Calling in a non-imported context is an error."""
        module = types.ModuleType("my_module")  # creates a new module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            @export
            def exported():
                pass
            """
        )
        with pytest.raises(ValueError):
            exec(module_code, module.__dict__)

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_dynamic(self):
        """The __all__ attr is created on the imported module if needed."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            @export
            def exported():
                pass
            """
        )
        exec(module_code, module.__dict__)

        imported = importlib.import_module("my_module")
        assert imported.__all__ == ["exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_dynamic_append(self):
        """The __all__ attr is appended to if it already exists."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            __all__ = ["first"]

            from pydecor.decorators import export

            first = "some other thing that is already exported"

            @export
            def exported():
                pass
            """
        )
        exec(module_code, module.__dict__)

        imported = importlib.import_module("my_module")
        assert imported.__all__ == ["first", "exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_dynamic_append_tuple(self):
        """If __all__ is a tuple, the generated one is still a tuple."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            __all__ = ("first",)

            from pydecor.decorators import export

            first = "some other thing that is already exported"

            @export
            def exported():
                pass
            """
        )
        exec(module_code, module.__dict__)

        imported = importlib.import_module("my_module")
        assert imported.__all__ == ("first", "exported")

    @pytest.mark.usefixtures("reset_modules")
    def test_export_idempotent_already_present(self):
        """The module is not added if already present."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            __all__ = ["exported"]

            from pydecor.decorators import export

            @export
            def exported():
                pass
            """
        )
        exec(module_code, module.__dict__)

        imported = importlib.import_module("my_module")
        assert imported.__all__ == ["exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_export_idempotent_multiple_calls(self):
        """Multiple calls don't hurt."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            @export
            @export
            def exported():
                pass
            """
        )
        exec(module_code, module.__dict__)

        imported = importlib.import_module("my_module")
        assert imported.__all__ == ["exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_static_no_all(self):
        """A module present in imports is manipulated correctly."""
        from .exports import no_all
        assert no_all.__all__ == ["exported"]  # pylint: disable=no-member

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_static_list_all(self):
        """A list __all__ is appended to."""
        from .exports import list_all
        assert list_all.__all__ == ["first", "exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_static_tuple_all(self):
        """A tuple __all__ is replaced with a new tuple."""
        from .exports import tuple_all
        assert tuple_all.__all__ == ("first", "exported")

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_static_class_export(self):
        """Classes may also be exported."""
        from .exports import class_export
        # pylint: disable=no-member
        assert class_export.__all__ == ["Exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_imported_module_static_multi_export(self):
        """Multiple items may be exported."""
        from .exports import multi_export
        # pylint: disable=no-member
        assert multi_export.__all__ == ["Exported", "exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_export_class_dynamic(self):
        """Classes may also be exported."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            @export
            class Exported:
                pass

            """
        )
        exec(module_code, module.__dict__)

        imported = importlib.import_module("my_module")
        assert imported.__all__ == ["Exported"]

    @pytest.mark.usefixtures("reset_modules")
    def test_export_instancemethod_fails(self):
        """Instance methods may not be exported directly."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            class BadClass:
                @export
                def foo(self):
                    pass

            """
        )
        with pytest.raises(TypeError):
            exec(module_code, module.__dict__)

    @pytest.mark.usefixtures("reset_modules")
    def test_export_classmethod_fails(self):
        """Classmethods may not be exported directly."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            class BadClass:
                @export
                @classmethod
                def foo(self):
                    pass

            """
        )
        with pytest.raises(TypeError):
            exec(module_code, module.__dict__)

    @pytest.mark.usefixtures("reset_modules")
    def test_export_staticmethod_fails(self):
        """Staticmethods may not be exported directly."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            class BadClass:
                @export
                @staticmethod
                def foo(self):
                    pass

            """
        )
        with pytest.raises(TypeError):
            exec(module_code, module.__dict__)

    @pytest.mark.usefixtures("reset_modules")
    @pytest.mark.parametrize("value", (
        "lambda: None",
        "'foo'",
        "12",
        "{}",
        "[]",
        "()",
        "set()",
        "None",
        "False",
        "range(5)",
        "iter(())",
    ))
    def test_export_failure_inline_expression(self, value):
        """Inline expressions are not valid input."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export
            export(lambda: None)
            """
        )
        with pytest.raises(TypeError):
            exec(module_code, module.__dict__)

    @pytest.mark.usefixtures("reset_modules")
    def test_export_failure_local_function(self):
        """Interior functions may not be exported."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            def foo():
                @export
                def inner():
                    pass

            foo()
            """
        )
        with pytest.raises(TypeError):
            exec(module_code, module.__dict__)

    @pytest.mark.usefixtures("reset_modules")
    def test_export_failure_class_instance(self):
        """Class instances may not be exported."""
        # In actual import machinery, the module is added to sys.modules
        # before the contained code is executed, so we mimic that here.
        module = module_from_spec(ModuleSpec("my_module", None))
        sys.modules["my_module"] = module

        module_code = textwrap.dedent(
            """
            from pydecor.decorators import export

            class Foo: pass

            foo = Foo()

            export(foo)
            """
        )
        with pytest.raises(TypeError):
            exec(module_code, module.__dict__)
