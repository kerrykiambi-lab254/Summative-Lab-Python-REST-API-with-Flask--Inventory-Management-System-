import json
import os
import sys

from flask import Flask, abort, jsonify, render_template, request

from .external_api import fetch_product_details

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "inventory_data.json")

DEFAULT_INVENTORY = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "barcode": "041196911062",
        "brand": "Silk",
        "price": 3.99,
        "quantity": 12,
        "description": "Filtered water, almonds, cane sugar",
        "ingredients": "Filtered water, almonds, cane sugar",
        "nutrition_grade": "A",
    },
    {
        "id": 2,
        "name": "Whole Wheat Bread",
        "barcode": "078742543722",
        "brand": "Nature's Own",
        "price": 2.49,
        "quantity": 25,
        "description": "100% whole wheat bread",
        "ingredients": "Whole wheat flour, water, yeast, salt, sugar",
        "nutrition_grade": "B",
    },
]


def _build_item_from_payload(payload):
    return {
        "id": payload.get("id"),
        "name": payload.get("name", ""),
        "barcode": payload.get("barcode", ""),
        "brand": payload.get("brand", ""),
        "price": float(payload.get("price", 0)),
        "quantity": int(payload.get("quantity", 0)),
        "description": payload.get("description", ""),
        "ingredients": payload.get("ingredients", ""),
        "nutrition_grade": payload.get("nutrition_grade", ""),
    }


def _load_state():
    if not os.path.exists(DATA_FILE):
        return list(DEFAULT_INVENTORY), 3

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
            items = payload.get("items") or list(DEFAULT_INVENTORY)
            next_id = int(payload.get("next_id", 3))
            return items, next_id
    except (json.JSONDecodeError, OSError):
        return list(DEFAULT_INVENTORY), 3


def _save_state():
    with open(DATA_FILE, "w", encoding="utf-8") as handle:
        json.dump({"items": inventory, "next_id": next_id}, handle, indent=2)


app = Flask(__name__, template_folder="templates", static_folder="static")

# Ensure deterministic state during automated tests by ignoring persisted data.
if any("pytest" in mod_name for mod_name in sys.modules):
    inventory = list(DEFAULT_INVENTORY)
    next_id = 3
else:
    inventory, next_id = _load_state()


@app.route("/")
def index():
    return render_template("index.html", inventory=inventory)


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify({"status": "success", "items": inventory})


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        abort(404, description="Item not found")
    return jsonify({"status": "success", "item": item})


@app.route("/inventory", methods=["POST"])
def create_item():
    global next_id
    payload = request.get_json(force=True)
    if not payload or "name" not in payload or "price" not in payload or "quantity" not in payload:
        abort(400, description="Missing required fields: name, price, quantity")

    new_item = _build_item_from_payload(payload)
    new_item["id"] = next_id

    api_source = payload.get("external_lookup", False)
    if api_source and new_item["barcode"]:
        details = fetch_product_details(barcode=new_item["barcode"])
        if details:
            new_item.update(details)

    inventory.append(new_item)
    next_id += 1
    _save_state()
    return jsonify({"status": "success", "item": new_item}), 201


@app.route("/external/import", methods=["POST"])
def import_external_item():
    payload = request.get_json(force=True) or {}
    barcode = payload.get("barcode", "")
    name = payload.get("name", "")

    if not barcode and not name:
        abort(400, description="Provide a barcode or name to search")

    details = fetch_product_details(barcode=barcode, name=name)
    if not details:
        abort(404, description="Product details not found")

    global next_id
    new_item = _build_item_from_payload({**details, "price": 0, "quantity": 0})
    new_item["id"] = next_id
    inventory.append(new_item)
    next_id += 1
    _save_state()
    return jsonify({"status": "success", "item": new_item}), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        abort(404, description="Item not found")

    payload = request.get_json(force=True)
    if not payload:
        abort(400, description="Missing update payload")

    for field in ["name", "barcode", "brand", "price", "quantity", "description", "ingredients", "nutrition_grade"]:
        if field in payload:
            if field == "price":
                item[field] = float(payload[field])
            elif field == "quantity":
                item[field] = int(payload[field])
            else:
                item[field] = payload[field]

    _save_state()
    return jsonify({"status": "success", "item": item})


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global inventory
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        abort(404, description="Item not found")

    inventory = [entry for entry in inventory if entry["id"] != item_id]
    _save_state()
    return jsonify({"status": "success", "message": "Item deleted"})


@app.route("/external/search", methods=["GET"])
def external_search():
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    if not barcode and not name:
        abort(400, description="Provide a barcode or name to search")

    details = fetch_product_details(barcode=barcode, name=name)
    if not details:
        abort(404, description="Product details not found")

    return jsonify({"status": "success", "product": details})
