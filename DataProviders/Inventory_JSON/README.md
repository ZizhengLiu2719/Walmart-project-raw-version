# Inventory Data Provider

This service provides CRUD (Create, Read, Update, Delete) operations for inventory data.  
It loads initial data from `data/inventory.json` into memory on startup.

## Requirements
- Python 3.8+
- FastAPI
- Uvicorn

Install dependencies:
```powershell
pip install fastapi uvicorn

Running the Service:
cd DataProviders\Inventory_JSON
uvicorn main:app --reload --port 8002

