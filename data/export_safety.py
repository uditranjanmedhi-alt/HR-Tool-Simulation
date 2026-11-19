"""Helpers for preventing spreadsheet formula execution in exported text cells."""

from __future__ import annotations

from math import isfinite


_FORMULA_PREFIXES = ("=", "+", "-", "@")


def safe_spreadsheet_cell(value):
    """Prefix formula-like strings while preserving numeric values."""
    if not isinstance(value, str):
        return value
    candidate = value.lstrip(" \t\r\n")
    if not candidate.startswith(_FORMULA_PREFIXES):
        return value
    try:
        numeric_value = float(candidate)
    except ValueError:
        return "'" + value
    return value if isfinite(numeric_value) else "'" + value
