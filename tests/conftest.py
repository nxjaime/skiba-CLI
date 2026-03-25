"""Pytest configuration for Skiba tests."""

import os
import sys

# Ensure skiba package is importable from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
