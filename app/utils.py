"""Utility functions for formatting and display."""

from decimal import Decimal


def ordinal(n: int) -> str:
    """Convert number to ordinal string (1 -> '1st', 2 -> '2nd', etc.)"""
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f'{n}{suffix}'


def rank_to_color(rank: int, total: int = 100) -> str:
    """Convert rank to hex color (green=best, red=worst)."""
    ratio = (rank - 1) / (total - 1) if total > 1 else 0
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    return f"#{r:02X}{g:02X}00"


def convert_floats_to_decimal(obj):
    """Convert floats to Decimals for DynamoDB writes."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    return obj


def convert_decimals_to_float(obj):
    """Convert Decimals back to floats for app use."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(i) for i in obj]
    return obj
