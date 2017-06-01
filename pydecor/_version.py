"""
version.py module

The version set here will be automatically incorporated into setup.py
and also set as the __version__ attribute for the package.
"""

__version_info__ = (0, 1, 0)
__version__ = '.'.join([str(ver) for ver in __version_info__])
