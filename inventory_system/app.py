"""Inventory Management System - Flask REST API."""

import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# In-memory inventory store
inventory = []
next_id = 1

EXTERNAL_API_URL = "https://fakestoreapi.com/products"


def find_item(item_id):
    """Find an inventory item by its ID. Returns (item, index) or (None, -1)."""
    for idx, item in enumerate(inventory):
        if item["id"] == item_id:
            return item, idx
    return None, -1


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Render the user interface."""
    return render_template("index.html")


@app.route("/items", methods=["GET"])
def get_items():
    """Return all inventory items."""
    return jsonify({"items": inventory, "count": len(inventory)}), 200


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Return a single inventory item by ID."""
    item, _ = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/items", methods=["POST"])
def create_item():
    """Create a new inventory item."""
    global next_id

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Item name is required and must be a non-empty string"}), 400

    category = data.get("category", "General")
    price = data.get("price", 0.0)
    quantity = data.get("quantity", 0)

    # Validate and coerce types
    try:
        price = float(price)
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"error": "Price must be a number and quantity must be an integer"}), 400

    if price < 0:
        return jsonify({"error": "Price cannot be negative"}), 400
    if quantity < 0:
        return jsonify({"error": "Quantity cannot be negative"}), 400

    item = {
        "id": next_id,
        "name": name.strip(),
        "category": category.strip() if isinstance(category, str) else "General",
        "price": price,
        "quantity": quantity,
    }
    inventory.append(item)
    next_id += 1

    return jsonify(item), 201


@app.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    """Partially update an inventory item."""
    item, idx = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Name must be a non-empty string"}), 400
        inventory[idx]["name"] = name.strip()

    if "category" in data:
        category = data["category"]
        if not isinstance(category, str) or not category.strip():
            return jsonify({"error": "Category must be a non-empty string"}), 400
        inventory[idx]["category"] = category.strip()

    if "price" in data:
        try:
            price = float(data["price"])
        except (ValueError, TypeError):
            return jsonify({"error": "Price must be a number"}), 400
        if price < 0:
            return jsonify({"error": "Price cannot be negative"}), 400
        inventory[idx]["price"] = price

    if "quantity" in data:
        try:
            quantity = int(data["quantity"])
        except (ValueError, TypeError):
            return jsonify({"error": "Quantity must be an integer"}), 400
        if quantity < 0:
            return jsonify({"error": "Quantity cannot be negative"}), 400
        inventory[idx]["quantity"] = quantity

    return jsonify(inventory[idx]), 200


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an inventory item."""
    item, idx = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    removed = inventory.pop(idx)
    return jsonify({"message": f"Item '{removed['name']}' deleted", "item": removed}), 200


@app.route("/fetch-external", methods=["POST"])
def fetch_external_products():
    """Fetch products from an external API and add them to the inventory."""
    global next_id

    try:
        response = requests.get(EXTERNAL_API_URL, timeout=10)
        response.raise_for_status()
        products = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch external products: {str(e)}"}), 502

    if not isinstance(products, list):
        return jsonify({"error": "Unexpected response format from external API"}), 502

    added = []
    for product in products:
        item = {
            "id": next_id,
            "name": product.get("title", "Unknown Product"),
            "category": product.get("category", "General"),
            "price": float(product.get("price", 0)),
            "quantity": 10,  # Default stock quantity for fetched items
        }
        inventory.append(item)
        added.append(item)
        next_id += 1

    return jsonify({"message": f"Added {len(added)} products from external API", "items": added}), 201


@app.route("/clear", methods=["POST"])
def clear_inventory():
    """Clear all inventory items (helper route for testing)."""
    global next_id
    inventory.clear()
    next_id = 1
    return jsonify({"message": "Inventory cleared"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
