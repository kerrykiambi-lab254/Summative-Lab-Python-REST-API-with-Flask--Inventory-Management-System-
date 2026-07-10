# Inventory Management System

A Flask-based REST API and admin portal for a retail inventory management system.

## Features

- CRUD inventory endpoints (`GET`, `POST`, `PATCH`, `DELETE`)
- External API integration with OpenFoodFacts-style product lookup
- CLI client for managing inventory via HTTP requests
- Web admin portal for browsing and managing items
- Unit tests for API routes, CLI interactions, and external API handling

## Requirements

- Python 3.11+
- Flask
- requests
- pytest

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Start the Flask app:

```powershell
python run.py
```

The admin portal will be available at `http://127.0.0.1:5000`.

## API Endpoints

- `GET /inventory` - fetch all inventory items
- `GET /inventory/<id>` - fetch a single item
- `POST /inventory` - create a new inventory item
- `PATCH /inventory/<id>` - update an existing item
- `DELETE /inventory/<id>` - remove an item
- `GET /external/search?barcode=<barcode>&name=<name>` - search external product details

## CLI Usage

Run the CLI from the project folder:

```powershell
python -m inventory_system.cli list
python -m inventory_system.cli view 1
python -m inventory_system.cli add --name "Organic Almond Milk" --barcode 041196911062 --price 3.99 --quantity 10
python -m inventory_system.cli update 1 --price 4.50 --quantity 15
python -m inventory_system.cli delete 1
python -m inventory_system.cli search --barcode 041196911062
```

## Testing

Run unit tests:

```powershell
python -m pytest
```
