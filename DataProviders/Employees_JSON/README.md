# Employees Data Provider

This service provides CRUD (Create, Read, Update, Delete) operations for employee data.  
It loads initial data from `data/employees.json` into memory on startup.

## Requirements
- Python 3.8+
- FastAPI
- Uvicorn

Install dependencies:
```powershell
pip install fastapi uvicorn

Running the Service:
cd DataProviders\Employees_JSON
uvicorn main:app --reload --port 8001


