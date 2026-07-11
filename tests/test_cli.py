import argparse
import json
import pytest
import requests

from inventory_system import cli

class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data


@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    def dummy_get(url, params=None, **kwargs):
        if url.endswith("/inventory"):
            return DummyResponse({"status": "success", "items": []})
        if url.endswith("/external/search"):
            return DummyResponse({"status": "success", "product": {"name": "Mock Item"}})
        return DummyResponse({"status": "success", "item": {"id": 1}})

    def dummy_post(url, json=None, **kwargs):
        return DummyResponse({"status": "success", "item": json}, 201)

    def dummy_patch(url, json=None, **kwargs):
        return DummyResponse({"status": "success", "item": json})

    def dummy_delete(url, **kwargs):
        return DummyResponse({"status": "success", "message": "Item deleted"})

    monkeypatch.setattr(requests, "get", dummy_get)
    monkeypatch.setattr(requests, "post", dummy_post)
    monkeypatch.setattr(requests, "patch", dummy_patch)
    monkeypatch.setattr(requests, "delete", dummy_delete)


def test_list_items(capsys):
    cli.list_items()
    captured = capsys.readouterr()
    assert "items" in captured.out


def test_view_item(capsys):
    cli.view_item(1)
    captured = capsys.readouterr()
    assert "id" in captured.out


def test_add_item(capsys):
    args = argparse.Namespace(name="New", barcode="123", price=1.99, quantity=5, external_lookup=False)
    cli.add_item(args)
    captured = capsys.readouterr()
    assert "New" in captured.out


def test_update_item(capsys):
    args = argparse.Namespace(id=1, name=None, barcode=None, price=2.5, quantity=10)
    cli.update_item(args)
    captured = capsys.readouterr()
    assert "2.5" in captured.out


def test_delete_item(capsys):
    cli.delete_item(1)
    captured = capsys.readouterr()
    assert "Item deleted" in captured.out


def test_search_external(capsys):
    args = argparse.Namespace(barcode="041196911062", name=None)
    cli.search_external(args)
    captured = capsys.readouterr()
    assert "Mock Item" in captured.out


def test_main_shows_food_logo(capsys, monkeypatch):
    # Trigger interactive menu path by omitting a subcommand
    monkeypatch.setattr("sys.argv", ["cli.py"])
    monkeypatch.setattr("builtins.input", lambda prompt=None: "1")
    cli.main()
    captured = capsys.readouterr()
    assert "PANTRY" in captured.out.upper()
    assert "Select an option" in captured.out



def test_list_items_handles_request_error(capsys, monkeypatch):
    def failing_get(url, params=None, **kwargs):
        raise requests.RequestException("offline")

    monkeypatch.setattr(requests, "get", failing_get)
    cli.list_items()
    captured = capsys.readouterr()
    assert "Unable to reach" in captured.out
