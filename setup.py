import os
import re
from setuptools import setup

NAME    = "knackhq"
AUTHOR  = "amancevice"
EMAIL   = "smallweirdnum@gmail.com"
DESC    = "Interact with KnackHQ API"

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities" ]
REQUIRES = [
    "certifi>=2016.2.28",
    "urllib3>=1.12" ]
TEST_REQUIRES = ["nose", "mock"]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def version():
    search = r"^__version__ *= *['\"]([0-9.]+)['\"]"
    initpy = read("./%s/__init__.py" % NAME)
    return re.search(search, initpy, re.MULTILINE).group(1)

setup(
    name                 = NAME,
    version              = version(),
    author               = AUTHOR,
    author_email         = EMAIL,
    packages             = [ NAME ],
    package_data         = { "%s" % NAME : ['README.md'] },
    include_package_data = True,
    url                  = 'http://www.smallweirdnumber.com',
    description          = DESC,
    long_description     = read('README.md'),
    classifiers          = CLASSIFIERS,
    install_requires     = REQUIRES,
    test_requires        = TEST_REQUIRES,
    test_suite           = "nose.collector" )
