import requests

MOCK_PRODUCTS = {
    "041196911062": {
        "name": "Organic Almond Milk",
        "brand": "Silk",
        "description": "Filtered water, almonds, cane sugar",
        "ingredients": "Filtered water, almonds, cane sugar",
        "nutrition_grade": "A",
        "barcode": "041196911062",
    },
    "078742543722": {
        "name": "Whole Wheat Bread",
        "brand": "Nature's Own",
        "description": "100% whole wheat bread",
        "ingredients": "Whole wheat flour, water, yeast, salt, sugar",
        "nutrition_grade": "B",
        "barcode": "078742543722",
    },
}

OPENFOODFACTS_BASE_URL = "https://world.openfoodfacts.org/api/v0/product"


def fetch_product_details(barcode: str | None = None, name: str | None = None) -> dict | None:
    if barcode and barcode in MOCK_PRODUCTS:
        return MOCK_PRODUCTS[barcode]

    if barcode:
        try:
            response = requests.get(f"{OPENFOODFACTS_BASE_URL}/{barcode}.json", timeout=5)
            response.raise_for_status()
            product = response.json().get("product", {})
            if product:
                return {
                    "name": product.get("product_name", ""),
                    "brand": product.get("brands", ""),
                    "description": product.get("generic_name", ""),
                    "ingredients": product.get("ingredients_text", ""),
                    "nutrition_grade": product.get("nutrition_grades", ""),
                    "barcode": barcode,
                }
        except requests.RequestException:
            return None

    if name:
        for item in MOCK_PRODUCTS.values():
            if item["name"].lower() == name.lower():
                return item

    return None
