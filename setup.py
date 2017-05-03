import os
import re
import textwrap
from setuptools import setup


def version():
    search = r"^__version__ *= *['\"]([0-9.]+)['\"]"
    initpy = open('./knackhq/__init__.py').read()
    return re.search(search, initpy, re.MULTILINE).group(1)


setup(name='knackhq',
      version=version(),
      author='amancevice',
      author_email='smallweirdnum@gmail.com',
      packages=['knackhq'],
      include_package_data=True,
      url='http://www.smallweirdnumber.com',
      description='Interact with KnackHQ API',
      long_description=textwrap.dedent(
          '''See GitHub_ for documentation.
          .. _GitHub: https://github.com/amancevice/knackhq'''),
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Utilities'],
      install_requires=['certifi>=2016.2.28',
                        'requests>=2.11.1'])
