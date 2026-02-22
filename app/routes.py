from flask import Blueprint, render_template, request, jsonify, Response, redirect, url_for
from typing import Any
from app.db import get_current, save_current

main = Blueprint('main', __name__)

@main.route("/")
def index() -> str:
    current = get_current()
    return render_template("index.html", current=current)

# @main.route("/data/<item_id>", methods=["GET"])
# def get_data(item_id: str) -> tuple[Response, int] | Response:
#     item = get_item(item_id)
#     if item:
#         return jsonify(item)
#     return jsonify({"error": "Not found"}), 404

@main.route("/data", methods=["POST"])
def create_data() -> Response:
    data: dict[str, Any] = {
        "value1": request.form.get("value1") + data["value1"],
        "value2": request.form.get("value2") + data["value2"],
        "value3": request.form.get("value3") + data["value3"],
    }
    save_current(data)
    return redirect(url_for("main.index"))
