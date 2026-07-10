import json
import pytest

from inventory_system.app import app, inventory, next_id

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_get_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert isinstance(data["items"], list)

def test_get_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["item"]["id"] == 1

def test_create_item(client):
    payload = {"name": "Test Product", "barcode": "000000000000", "price": 1.99, "quantity": 5}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["item"]["name"] == "Test Product"

def test_update_item(client):
    response = client.patch("/inventory/1", json={"price": 4.50, "quantity": 8})
    assert response.status_code == 200
    data = response.get_json()
    assert data["item"]["price"] == 4.50
    assert data["item"]["quantity"] == 8

def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Item deleted"

def test_get_missing_item(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404

def test_create_missing_fields(client):
    response = client.post("/inventory", json={"name": "Incomplete"})
    assert response.status_code == 400


def test_import_external_item(client):
    response = client.post("/external/import", json={"barcode": "041196911062"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["item"]["name"] == "Organic Almond Milk"
