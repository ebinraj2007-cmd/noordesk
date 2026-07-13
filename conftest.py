"""Make the project importable no matter how pytest is invoked.

Ensures `noordesk` and `webapp` are on sys.path so `pytest tests/` works the
same as `python -m pytest` (needed for CI).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
