# This file makes the layer1_uninformed folder a Python package

from .bfs import bfs
from .dfs import dfs
from .ucs import ucs

__all__ = ['bfs', 'dfs', 'ucs']