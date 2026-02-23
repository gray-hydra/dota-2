"""Business logic for ranking and value calculations."""

import random
from app.utils import rank_to_color, ordinal


# Value calculation formulas
def calc_value7(tk: float, td: float) -> float:
    return tk / td


def calc_value8(tk: float, ta: float, tg: float) -> float:
    return (tk + (ta / 2)) / tg


def calc_value9(tk: float, ta: float, td: float) -> float:
    return ((tk * 10) + (ta * 5)) / td


def calc_value10(tg: float, tk: float, td: float, ta: float, tc: float, tn: float) -> float:
    return ((tk * 10) + (ta * 5) + (tc - tn) - (td * 10)) / tg


# Ranking functions
def compute_ranks(items: list, value_key: str, higher_is_better: bool = True) -> list:
    """Add rank field to each item based on value_key (rank 1 = best)."""
    sorted_items = sorted(items, key=lambda x: x[value_key], reverse=higher_is_better)
    for rank, item in enumerate(sorted_items, start=1):
        item[f'rank_{value_key}'] = rank
    return items


def compute_value11(items: list) -> list:
    """Compute value11 as aggregate of ranks 2-10, with value3 and value6 inverted."""
    n = len(items)
    for item in items:
        # Normal ranks (lower rank = better)
        normal = (
            item['rank_value2'] +
            item['rank_value4'] +
            item['rank_value5'] +
            item['rank_value7'] +
            item['rank_value8'] +
            item['rank_value9'] +
            item['rank_value10']
        )
        # Inverted ranks (rank 1 becomes n, rank n becomes 1)
        inverted = (
            (n + 1 - item['rank_value3']) +
            (n + 1 - item['rank_value6'])
        )
        item['value11'] = normal + inverted
    return items


def pick_from_quintiles(team_items: list, rank_key: str, total_items: int) -> list:
    """Pick one random item from each overall quintile (5 items total).

    Quintiles are based on total_items, not len(team_items).
    Q1: ranks 1-20, Q2: 21-40, etc. (for 100 total items)
    """
    quintile_size = total_items // 5

    picked = []
    for q in range(5):
        min_rank = q * quintile_size + 1
        max_rank = (q + 1) * quintile_size if q < 4 else total_items

        # Find team items in this quintile
        in_quintile = [i for i in team_items if min_rank <= i[rank_key] <= max_rank]

        if in_quintile:
            picked.append(random.choice(in_quintile))

    return picked


# Formatting functions
def format_ranks_as_ordinals(items: list, total: int = 100) -> list:
    """Convert all rank fields to ordinal strings and add colors."""
    for item in items:
        for key in list(item.keys()):
            if key.startswith('rank_'):
                rank = item[key]
                color_key = key.replace('rank_', 'color_')
                item[color_key] = rank_to_color(rank, total)
                item[key] = ordinal(rank)
    return items


def add_colors_only(items: list, total: int = 100) -> list:
    """Add color fields without converting ranks to ordinals (keep numeric for sorting)."""
    for item in items:
        for key in list(item.keys()):
            if key.startswith('rank_'):
                rank = item[key]
                color_key = key.replace('rank_', 'color_')
                item[color_key] = rank_to_color(rank, total)
    return items


def calculate_derived_values(item: dict) -> dict:
    """Calculate value7-10 from input values 1-6."""
    tg = item['value1']
    tk = item['value2']
    td = item['value3']
    ta = item['value4']
    tc = item['value5']
    tn = item['value6']

    # Avoid division by zero
    if td < 1:
        td = 1
    if tg < 1:
        tg = 1

    item['value7'] = calc_value7(tk, td)
    item['value8'] = calc_value8(tk, ta, tg)
    item['value9'] = calc_value9(tk, ta, td)
    item['value10'] = calc_value10(tg, tk, td, ta, tc, tn)

    return item
