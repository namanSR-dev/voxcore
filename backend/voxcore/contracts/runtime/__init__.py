"""
Runtime Contract Package

Contains pure data structures representing the core domain entities exchanged between packages.
"""
from .models import Request, Response

__all__ = ["Request", "Response"]
