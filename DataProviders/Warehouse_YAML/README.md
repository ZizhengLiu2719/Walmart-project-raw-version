# Warehouse Inventory Management System

## Quick Start

```
# From the Warehouse_YAML folder
python -m pip install -r requirements.txt

# Start with python:
python main.py

# Or with uvicorn (recommended for production/dev):
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Warehouse Management

- **GET /warehouses**

  - List all warehouses
  - Returns: YAML list of all warehouses and their inventories

- **GET /warehouses/{warehouse_id}**

  - Get details of a specific warehouse
  - Returns: YAML warehouse data

- **POST /warehouses**

  - Create a new warehouse
  - Body: YAML warehouse data
  - Example:
    ```yaml
    warehouse_id: WH003
    name: South Distribution Center
    location: 567 Logistics Avenue, Dallas TX
    last_updated: 2025-08-26
    inventory: [] # Optional initial inventory
    ```

- **PUT /warehouses/{warehouse_id}**

  - Update warehouse information
  - Body: YAML warehouse data (same format as POST)

- **DELETE /warehouses/{warehouse_id}**
  - Delete a warehouse and its inventory

### Warehouse Inventory Management

- **GET /warehouses/{warehouse_id}/inventory**

  - List all items in a warehouse
  - Returns: YAML inventory list

- **POST /warehouses/{warehouse_id}/inventory**

  - Add new item to warehouse
  - Body: YAML item data
  - Example:
    ```yaml
    item_id: 1007
    name: Graphics Card
    category: Computers
    quantity: 200
    unit_price: 579.99
    supplier: WEN Corp
    restock_date: 2025-09-10 # Optional
    ```

- **PUT /warehouses/{warehouse_id}/inventory/{item_id}**

  - Update item in warehouse
  - Body: YAML item data (same format as POST)

- **DELETE /warehouses/{warehouse_id}/inventory/{item_id}**
  - Remove item from warehouse

## Data Validation

The system validates:

- Required fields for warehouses and items
- Data types (integers, floats, dates)
- Non-negative quantities and prices
- Unique warehouse IDs and item IDs within warehouses
- Valid YAML formatting

## Error Handling

All error responses include detailed error messages in YAML format.

## Notes

- All responses are in YAML format
- The system maintains data in memory, so the starting yaml never changes intentionally
