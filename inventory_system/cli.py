import argparse
import json
import requests

API_BASE = "http://127.0.0.1:5000"


def print_banner():
    print(
        """
┌────────────────────────────────────┐
│   PANTRY PORTAL CLI                │
│   Fresh stock, quick pantry picks  │
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


def list_items():
    data = _request_json(requests.get, f"{API_BASE}/inventory")
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
        print("1) list")
        print("2) view")
        print("3) add")
        print("4) update")
        print("5) delete")
        print("6) search")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            list_items()
        elif choice == "2":
            item_id = int(input("Enter item id: ").strip())
            view_item(item_id)
        elif choice == "3":
            name = input("Enter name: ").strip()
            barcode = input("Enter barcode (optional): ").strip()
            price = float(input("Enter price: ").strip())
            quantity = int(input("Enter quantity: ").strip())
            external_lookup = input("External lookup? (y/n): ").strip().lower() == "y"
            add_item(argparse.Namespace(
                name=name,
                barcode=barcode,
                price=price,
                quantity=quantity,
                external_lookup=external_lookup,
            ))
        elif choice == "4":
            item_id = int(input("Enter item id: ").strip())
            name = input("Enter new name (optional): ").strip() or None
            barcode = input("Enter new barcode (optional): ").strip() or None
            price_raw = input("Enter new price (optional): ").strip()
            quantity_raw = input("Enter new quantity (optional): ").strip()
            price = float(price_raw) if price_raw else None
            quantity = int(quantity_raw) if quantity_raw else None
            update_item(argparse.Namespace(
                id=item_id,
                name=name,
                barcode=barcode,
                price=price,
                quantity=quantity,
            ))
        elif choice == "5":
            item_id = int(input("Enter item id: ").strip())
            delete_item(item_id)
        elif choice == "6":
            barcode = input("Enter barcode (optional): ").strip() or None
            name = input("Enter name (optional): ").strip() or None
            search_external(argparse.Namespace(barcode=barcode, name=name))
        else:
            print("Invalid choice.")
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
