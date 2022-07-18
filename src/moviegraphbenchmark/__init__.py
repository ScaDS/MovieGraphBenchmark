import sys
import logging
from .loading import load_data
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

__all__ = ["load_data"]
