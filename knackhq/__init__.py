"""
KnackHQ API Client
"""
import pkg_resources

from knackhq.knackhq import KnackApp  # noqa: F401
from knackhq import exceptions  # noqa: F401

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = None
