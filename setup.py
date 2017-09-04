# -*- coding: UTF-8 -*-
"""
setup module for ihiji_schemas
"""

from os.path import dirname, join, realpath
from setuptools import setup, find_packages
from textwrap import dedent


fdir = dirname(realpath(__file__))


NAME = 'pydecor'
URL = 'https://github.com/mplanchard/pydecor'
AUTHOR = 'Matthew Planchard'
EMAIL = 'msplanchard@gmail.com'


SHORT_DESC = 'Easy peasy Python decorators'

LONG_DESC = dedent(
    '''
    Decorators are great, but they're hard to write, especially if you want
    to include arguments to your decorators, or use your decorators on
    class methods as well as functions. I know that, no matter how many I 
    write, I still find myself looking up the syntax every time. And that's 
    just for simple function decorators. Getting decorators to work 
    consistently at the class and method level is a whole 'nother barrel 
    of worms.

    PyDecor aims to make function decoration easy and straightforward, so that
    developers can stop worrying about closures and syntax in triply nested
    functions and instead get down to decorating!
    '''
)


KEYWORDS = [
    'decorators',
    'python2',
    'python3',
]


PACKAGE_DEPENDENCIES = []
SETUP_DEPENDENCIES = []
TEST_DEPENDENCIES = []
EXTRAS_DEPENDENCIES = {}

ENTRY_POINTS = {}

with open(join(fdir, 'requirements.txt')) as reqfile:
    for ln in reqfile:
        if not ln.startswith('#'):
            PACKAGE_DEPENDENCIES.append(ln.strip())

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for all
# available setup classifiers
CLASSIFIERS = [
    # 'Development Status :: 1 - Planning',
    # 'Development Status :: 2 - Pre-Alpha',
    # 'Development Status :: 3 - Alpha',
    # 'Development Status :: 4 - Beta',
    'Development Status :: 5 - Production/Stable',
    # 'Development Status :: 6 - Mature',
    # 'Framework :: AsyncIO',
    # 'Framework :: Flask',
    # 'Framework :: Sphinx',
    # 'Environment :: Web Environment',
    'Intended Audience :: Developers',
    # 'Intended Audience :: End Users/Desktop',
    # 'Intended Audience :: Science/Research',
    # 'Intended Audience :: System Administrators',
    # 'License :: Other/Proprietary License',
    # 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    # 'Operating System :: MacOS :: MacOS X
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    # 'Programming Language :: Python :: 3 :: Only',
    # 'Programming Language :: Python :: Implementation :: PyPy',
]


__version__ = '0.0.0'

with open(join(fdir, '{0}/_version.py'.format(NAME))) as version_file:
    for line in version_file:
        # This will populate the __version__ and __version_info__ variables
        if line.startswith('__'):
            exec(line)

setup(
    name=NAME,
    version=__version__,
    description=SHORT_DESC,
    long_description=LONG_DESC,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=find_packages(exclude=['*.tests', '*.tests.*']),
    install_requires=PACKAGE_DEPENDENCIES,
    setup_requires=SETUP_DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    extras_require=EXTRAS_DEPENDENCIES,
)
