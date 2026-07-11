import argparse
import json
import requests

API_BASE = "http://127.0.0.1:5000"


def print_banner():
    print(
        """
┌────────────────────────────────────┐
│            PANTRY STORE CLI       │
│   Fresh stock, quick pantry picks │
└────────────────────────────────────┘
"""
    )


def _request_json(request_fn, url, **kwargs):
    try:
        response = request_fn(url, **kwargs)
        if hasattr(response, "status_code") and getattr(response, "status_code", 200) >= 400:
            return {
                "status": "error",
                "message": f"Request failed with status {response.status_code}",
            }
        return response.json()
    except requests.RequestException as exc:
        return {
            "status": "error",
            "message": f"Unable to reach Pantry API: {exc}",
        }


def _sort_items(items):
    if not isinstance(items, list):
        return items

    def key(it):
        return (
            str(it.get("category", "")).strip().lower(),
            str(it.get("product_name", "")).strip().lower(),
            it.get("id", 0),
        )

    try:
        return sorted(items, key=key)
    except TypeError:
        return items


def list_items():
    data = _request_json(requests.get, f"{API_BASE}/inventory")
    if isinstance(data, dict) and "items" in data:
        data["items"] = _sort_items(data["items"])
    print(json.dumps(data, indent=2))


def view_item(item_id: int):
    data = _request_json(requests.get, f"{API_BASE}/inventory/{item_id}")
    print(json.dumps(data, indent=2))


def add_item(args):
    payload = {
        "name": args.name,
        "barcode": args.barcode,
        "price": args.price,
        "quantity": args.quantity,
        "external_lookup": args.external_lookup,
    }
    data = _request_json(requests.post, f"{API_BASE}/inventory", json=payload)
    print(json.dumps(data, indent=2))


def update_item(args):
    payload = {}
    if args.name:
        payload["name"] = args.name
    if args.barcode:
        payload["barcode"] = args.barcode
    if args.price is not None:
        payload["price"] = args.price
    if args.quantity is not None:
        payload["quantity"] = args.quantity
    data = _request_json(requests.patch, f"{API_BASE}/inventory/{args.id}", json=payload)
    print(json.dumps(data, indent=2))


def delete_item(item_id: int):
    data = _request_json(requests.delete, f"{API_BASE}/inventory/{item_id}")
    print(json.dumps(data, indent=2))


def search_external(args):
    params = {}
    if args.barcode:
        params["barcode"] = args.barcode
    if args.name:
        params["name"] = args.name
    data = _request_json(requests.get, f"{API_BASE}/external/search", params=params)
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Food-themed inventory management CLI")
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("list", help="List all inventory items")

    view_parser = subparsers.add_parser("view", help="View inventory item")
    view_parser.add_argument("id", type=int)

    add_parser = subparsers.add_parser("add", help="Add new inventory item")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--barcode", default="")
    add_parser.add_argument("--price", type=float, required=True)
    add_parser.add_argument("--quantity", type=int, required=True)
    add_parser.add_argument("--external-lookup", action="store_true")

    update_parser = subparsers.add_parser("update", help="Update item")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("--name")
    update_parser.add_argument("--barcode")
    update_parser.add_argument("--price", type=float)
    update_parser.add_argument("--quantity", type=int)

    delete_parser = subparsers.add_parser("delete", help="Delete inventory item")
    delete_parser.add_argument("id", type=int)

    search_parser = subparsers.add_parser("search", help="Search external API")
    search_parser.add_argument("--barcode")
    search_parser.add_argument("--name")

    args = parser.parse_args()
    print_banner()

    # Interactive selection menu (used when no subcommand is provided)
    if not getattr(args, "command", None):
        print("\nSelect an option:")
        print("1) Create")
        print("2) Read")
        print("3) Update")
        print("4) Delete")
        print("5) Count Records")
        print("6) Clear All")
        print("7) Search")
        print("8) Sort Records")
        print("9) Exit")

        choice = input("Enter choice (1-9): ").strip()

        # Implement only choices 1 and 2 (as requested)
        if choice == "1":
            # Create (add item)
            name = input("Enter name: ").strip()
            barcode = input("Enter barcode (optional): ").strip()
            price = float(input("Enter price: ").strip())
            quantity = int(input("Enter quantity: ").strip())
            external_lookup = input("External lookup? (y/n): ").strip().lower() == "y"
            add_item(
                argparse.Namespace(
                    name=name,
                    barcode=barcode,
                    price=price,
                    quantity=quantity,
                    external_lookup=external_lookup,
                )
            )
        elif choice == "2":
            # Read (list items)
            list_items()
        else:
            print("Not implemented yet.")
        return

    if args.command == "list":
        list_items()
    elif args.command == "view":
        view_item(args.id)
    elif args.command == "add":
        add_item(args)
    elif args.command == "update":
        update_item(args)
    elif args.command == "delete":
        delete_item(args.id)
    elif args.command == "search":
        search_external(args)



if __name__ == "__main__":
    main()
