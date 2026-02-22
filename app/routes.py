from flask import Blueprint, render_template, request, jsonify, Response, redirect, url_for, current_app
from typing import Any
import json
import random

main = Blueprint('main', __name__)

DATA_FILE = 'data/items.json'

def load_items() -> list:
    with open(DATA_FILE) as f:
        return json.load(f)

def save_items(items: list) -> None:
    with open(DATA_FILE, 'w') as f:
        json.dump(items, f, indent=4)

def rank_to_color(rank: int, total: int = 100) -> str:
    """Convert rank to hex color (green=best, red=worst)"""
    ratio = (rank - 1) / (total - 1) if total > 1 else 0
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    return f"#{r:02X}{g:02X}00"

def calc_value7(tk: float, td: float) -> float:
    return tk / td

def calc_value8(tk: float, ta: float, tg: float) -> float:
    return (tk + (ta / 2)) / tg

def calc_value9(tk: float, ta: float, td: float) -> float:
    return ((tk * 10) + (ta * 5)) / td

def calc_value10(tg: float, tk: float, td: float, ta: float, tc: float, tn: float) -> float:
    return ((tk * 10) + (ta * 5) + (tc - tn) - (td * 10)) / tg

def ordinal(n: int) -> str:
    """Convert number to ordinal string (1 -> '1st', 2 -> '2nd', etc.)"""
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f'{n}{suffix}'

def compute_ranks(items: list, value_key: str, higher_is_better: bool = True) -> list:
    """Add rank field to each item based on value_key (rank 1 = best)"""
    sorted_items = sorted(items, key=lambda x: x[value_key], reverse=higher_is_better)
    for rank, item in enumerate(sorted_items, start=1):
        item[f'rank_{value_key}'] = rank  # numeric for sorting
    return items

def compute_value11(items: list) -> list:
    """Compute value11 as aggregate of ranks 2-10, with value3 and value6 inverted"""
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
    """Pick one random item from each overall quintile (5 items total)

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

def format_ranks_as_ordinals(items: list, total: int = 100) -> list:
    """Convert all rank fields to ordinal strings and add colors"""
    for item in items:
        for key in list(item.keys()):
            if key.startswith('rank_'):
                rank = item[key]
                color_key = key.replace('rank_', 'color_')
                item[color_key] = rank_to_color(rank, total)
                item[key] = ordinal(rank)
    return items

def add_colors_only(items: list, total: int = 100) -> list:
    """Add color fields without converting ranks to ordinals (keep numeric for sorting)"""
    for item in items:
        for key in list(item.keys()):
            if key.startswith('rank_'):
                rank = item[key]
                color_key = key.replace('rank_', 'color_')
                item[color_key] = rank_to_color(rank, total)
    return items

@main.route("/")
def index() -> str:
    return render_template("index.html")

@main.route("/view")
def view() -> str:
    return render_template("view.html")

@main.route("/all")
def all_items() -> Response:
    items = load_items()

    # Compute ranks across ALL items
    items = compute_ranks(items, 'value1')
    items = compute_ranks(items, 'value2')
    items = compute_ranks(items, 'value3')
    items = compute_ranks(items, 'value4')
    items = compute_ranks(items, 'value5')
    items = compute_ranks(items, 'value6')
    items = compute_ranks(items, 'value7')
    items = compute_ranks(items, 'value8')
    items = compute_ranks(items, 'value9')
    items = compute_ranks(items, 'value10')
    items = compute_value11(items)
    items = compute_ranks(items, 'value11', higher_is_better=False)

    # Add colors but keep numeric ranks for sorting
    add_colors_only(items, len(items))

    return jsonify({"items": items})

@main.route("/generate")
def generate() -> Response:
    items = load_items()

    # Compute ranks across ALL items for each field
    items = compute_ranks(items, 'value2')
    items = compute_ranks(items, 'value3')
    items = compute_ranks(items, 'value4')
    items = compute_ranks(items, 'value5')
    items = compute_ranks(items, 'value6')
    items = compute_ranks(items, 'value7')
    items = compute_ranks(items, 'value8')
    items = compute_ranks(items, 'value9')
    items = compute_ranks(items, 'value10')

    # Compute value11 from aggregated ranks
    items = compute_value11(items)
    items = compute_ranks(items, 'value11', higher_is_better=False)  # lower sum = better

    # Split by team
    team_a = [i for i in items if i['team'] == 'A']
    team_b = [i for i in items if i['team'] == 'B']

    # Pick 5 from each team using overall quintiles (based on value11 rank)
    total = len(items)
    selected_a = pick_from_quintiles(team_a, 'rank_value11', total)
    selected_b = pick_from_quintiles(team_b, 'rank_value11', total)

    # Convert numeric ranks to ordinals and add colors
    format_ranks_as_ordinals(selected_a, total)
    format_ranks_as_ordinals(selected_b, total)

    return jsonify({"teamA": selected_a, "teamB": selected_b})

@main.route("/save", methods=["POST"])
def save() -> Response:
    data = request.get_json()
    item_id = data['id']

    items_list = load_items()
    items_map = {item['id']: item for item in items_list}

    # Update the item
    item = items_map[item_id]
    item['value1'] += data['value1']
    item['value2'] += data['value2']
    item['value3'] += data['value3']
    item['value4'] += data['value4']
    item['value5'] += data['value5']
    item['value6'] += data['value6']

    # Derived values
    tg = item['value1']
    tk = item['value2']
    td = item['value3']
    ta = item['value4']
    tc = item['value5']
    tn = item['value6']
    if td < 1: td = 1  # can't divide by 0
    if tg < 1: tg = 1  # can't divide by 0

    item['value7'] = calc_value7(tk, td)
    item['value8'] = calc_value8(tg, tk, ta)
    item['value9'] = calc_value9(tk, ta, td)
    item['value10'] = calc_value10(tg, tk, td, ta, tc, tn)

    # Convert back to array and save
    items_list = list(items_map.values())
    save_items(items_list)

    current_app.logger.info(f"Saved item {item_id}: {data}")
    return jsonify({"success": True})
