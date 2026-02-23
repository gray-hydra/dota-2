from flask import Blueprint, render_template, request, jsonify, Response, current_app

from app.data import load_items, save_items
from app.services import (
    compute_ranks,
    compute_value11,
    pick_from_quintiles,
    format_ranks_as_ordinals,
    add_colors_only,
    calculate_derived_values,
)

main = Blueprint('main', __name__)


@main.route("/health")
def health() -> Response:
    """Health check endpoint for container orchestration."""
    return jsonify({"status": "healthy"})


@main.route("/")
def index() -> str:
    return render_template("index.html")

@main.route("/generate-page")
def generate_page() -> str:
    return render_template("generate.html")

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

    # Calculate derived values
    calculate_derived_values(item)

    # Convert back to array and save
    items_list = list(items_map.values())
    save_items(items_list)

    current_app.logger.info(f"Saved item {item_id}: {data}")
    return jsonify({"success": True})
