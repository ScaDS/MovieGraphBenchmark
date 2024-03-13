import sys
import logging
from .loading import load_data

from importlib.metadata import version  # pragma: no cover

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

__all__ = ["load_data"]
__version__ = version(__package__)
