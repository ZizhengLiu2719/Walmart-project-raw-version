# Distribution Management System

## Quick Start

```
# From the Distribution_YAML folder
python -m pip install -r requirements.txt

# Start with python:
python main.py

# Or with uvicorn (recommended for production/dev):
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Distribution Management

- **GET /orders**
  - List all orders
  - Returns: YAML list of all orders and their items

- **GET /orders/{order_id}**
  - Get details of a specific order
  - Returns: YAML order data

- **POST /orders**
  - Create a new order
  - Body: YAML order data
  - Example:
    ```yaml
    order_id: 10002
    origin: Taiwan
    destination: WH002
    status: in-transit
    departure_date: 2025-08-29
    estimated_arrival: 2025-09-12
    items: []  # Optional items
    ```

- **PUT /orders/{order_id}**
  - Update order information
  - Body: YAML order data (same format as POST)

- **DELETE /orders/{order_id}**
  - Delete a order and its items

### Order Item Management

- **GET /orders/{order_id}/items**
  - List all items in a order
  - Returns: YAML items list

- **POST /orders/{order_id}/items**
  - Add new item to order
  - Body: YAML item data
  - Example:
    ```yaml
        item_id: 1008
        name: Semiconductors
        category: Processers
        quantity: 300
        unit_price: 170.10
        supplier: ConductINC
    ```

- **PUT /orders/{order_id}/items/{item_id}**
  - Update item in order
  - Body: YAML item data (same format as POST)

- **DELETE /orders/{order_id}/items/{item_id}**
  - Remove item from order



## Data Validation

The system validates:
- Required fields for orders and items
- Data types (integers, floats, dates)
- Non-negative quantities and prices
- Unique order IDs and item IDs within orders
- Valid YAML formatting

## Error Handling
All error responses include detailed error messages in YAML format.

## Notes
- All responses are in YAML format
- The system maintains data in memory, so the starting yaml never changes intentonally
- `last_updated` is automatically managed for changes
