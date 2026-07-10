import pytest
from inventory_system.external_api import fetch_product_details, MOCK_PRODUCTS


def test_fetch_product_details_by_barcode_from_mock():
    result = fetch_product_details(barcode="041196911062")
    assert result is not None
    assert result["name"] == "Organic Almond Milk"


def test_fetch_product_details_by_name_from_mock():
    result = fetch_product_details(name="Whole Wheat Bread")
    assert result is not None
    assert result["brand"] == "Nature's Own"


def test_fetch_product_details_missing():
    result = fetch_product_details(barcode="000000000000")
    assert result is None
