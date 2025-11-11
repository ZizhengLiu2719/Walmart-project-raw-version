from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import date
import yaml

class InventoryItem(BaseModel):
    item_id: int
    name: str
    category: str
    quantity: int = Field(ge=0)  # Ensure quantity is non-negative
    unit_price: float = Field(ge=0.0)  # Ensure price is non-negative
    supplier: str

class Orders(BaseModel):
    order_id: int
    origin: str
    destination: str
    status: str
    departure_date: date
    estimated_arrival: date
    items: List[InventoryItem] = []

app = FastAPI()

# In-memory order store
orders: Dict[str, Orders] = {}

# Load orders from YAML file
with open('data/dc.yaml', 'r') as file:
    data = yaml.safe_load(file)
    
    if not isinstance(data, dict) or 'orders' not in data or not isinstance(data['orders'], list):
        raise ValueError("Invalid order.yaml format. Expected 'orders' list at root level.")
        
    for order_data in data['orders']:
        try:
            # Convert inventory items to proper format if present
            if 'item' in order_data:
                inventory_items = [InventoryItem(**item) for item in order_data['item']]
                order_data['item'] = inventory_items
                
            # Create and store order object
            order = Orders(**order_data)
            orders[order.order_id] = order
        except ValueError as e:
            print(f"Error loading order: {e}")

@app.get("/orders", response_class=PlainTextResponse)
async def get_orders():
    """
    Retrieve a list of all orders in the system.
    
    Returns:
        PlainTextResponse: YAML formatted string containing all order information
    """
    return yaml.dump({"orders": [w.model_dump() for w in orders.values()]}, sort_keys=False)

@app.get("/orders/{order_id}", response_class=PlainTextResponse)
async def get_order(order_id: int):
    """
    Retrieve information about a specific order.
    
    Args:
        order_id (int): The unique identifier of the order
    
    Returns:
        PlainTextResponse: YAML formatted string containing the order information
    
    Raises:
        HTTPException: 404 if order is not found
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="order not found")
    return yaml.dump(orders[order_id].model_dump(), sort_keys=False)

@app.post("/orders", response_class=PlainTextResponse)
async def add_order(request: Request):
    """
    Create a new order in the system.
    
    Args:
        request (Request): FastAPI request object containing YAML formatted order data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming order creation
    
    Raises:
        HTTPException: 400 if YAML is invalid or order ID already exists
    """
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        if data is None:
            raise HTTPException(status_code=400, detail="body must not be empty")
        order = Orders(**data)
        if order.order_id in orders:
            raise HTTPException(status_code=400, detail="order ID already exists")
        orders[order.order_id] = order
        return yaml.dump({"message": "order added", "order": order.model_dump()}, sort_keys=False)
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/orders/{order_id}", response_class=PlainTextResponse)
async def update_order(order_id: int, request: Request):
    """
    Update an existing order's information.
    
    Args:
        order_id (int): The unique identifier of the order to update
        request (Request): FastAPI request object containing YAML formatted order data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming order update
    
    Raises:
        HTTPException: 404 if order not found, 400 if YAML is invalid or IDs don't match
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="order not found")
    
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        updated_order = Orders(**data)
        if updated_order.order_id != order_id:
            raise HTTPException(status_code=400, detail="order ID in URL does not match payload")
        orders[order_id] = updated_order
        return yaml.dump({"message": "order updated", "order": updated_order.model_dump()}, sort_keys=False)
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/orders/{order_id}", response_class=PlainTextResponse)
async def delete_order(order_id: int):
    """
    Delete a order from the system.
    
    Args:
        order_id (int): The unique identifier of the order to delete
    
    Returns:
        PlainTextResponse: YAML formatted string confirming order deletion
    
    Raises:
        HTTPException: 404 if order not found
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="order not found")
    del orders[order_id]
    return yaml.dump({"message": f"order {order_id} deleted"}, sort_keys=False)

# item management within orders
@app.get("/orders/{order_id}/items", response_class=PlainTextResponse)
async def get_order_item(order_id: int):
    """
    Retrieve the item list for a specific order.
    
    Args:
        order_id (int): The unique identifier of the order
    
    Returns:
        PlainTextResponse: YAML formatted string containing the order's items
    
    Raises:
        HTTPException: 404 if order not found
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="order not found")
    return yaml.dump({"items": [item.model_dump() for item in orders[order_id].items]}, sort_keys=False)

@app.post("/orders/{order_id}/items", response_class=PlainTextResponse)
async def add_order_item(order_id: int, request: Request):
    """
    Add a new item to a specific order.
    
    Args:
        order_id (int): The unique identifier of the order
        request (Request): FastAPI request object containing YAML formatted item data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming item addition
    
    Raises:
        HTTPException: 404 if order not found, 400 if YAML is invalid or item ID exists
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="order not found")
    
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        if data is None:
            raise HTTPException(status_code=400, detail="body must not be empty")
        item = InventoryItem(**data)
        order = orders[order_id]
        # Check if item already exists
        if any(existing.item_id == item.item_id for existing in order.items):
            raise HTTPException(status_code=400, detail="Item ID already exists in this order")
        order.items.append(item)
        return yaml.dump({"message": "Item added", "item": item.model_dump()}, sort_keys=False)
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/orders/{order_id}/items/{item_id}", response_class=PlainTextResponse)
async def update_order_item(order_id: int, item_id: int, request: Request):
    """
    Update an existing item in a specific order.
    
    Args:
        order_id (int): The unique identifier of the order
        item_id (int): The unique identifier of the item to update
        request (Request): FastAPI request object containing YAML formatted item data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming item update
    
    Raises:
        HTTPException: 404 if order or item not found, 400 if YAML is invalid or IDs don't match
    """

    if order_id not in orders:
        raise HTTPException(status_code=404, detail="order not found")
    
    order = orders[order_id]
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        updated_item = InventoryItem(**data)
        if updated_item.item_id != item_id:
            raise HTTPException(status_code=400, detail="Item ID in URL does not match payload")
        
        for i, item in enumerate(order.items):
            if item.item_id == item_id:
                order.items[i] = updated_item
                return yaml.dump({"message": "Item updated", "item": updated_item.model_dump()}, sort_keys=False)
        raise HTTPException(status_code=404, detail="Item not found in order")
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/orders/{order_id}/item/{item_id}", response_class=PlainTextResponse)
async def delete_order_item(order_id: int, item_id: int):
    """
    Delete an item from a specific order.
    
    Args:
        order_id (int): The unique identifier of the order
        item_id (int): The unique identifier of the item to delete
    
    Returns:
        PlainTextResponse: YAML formatted string confirming item deletion
    
    Raises:
        HTTPException: 404 if order or item not found
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="order not found")
    
    order = orders[order_id]
    original_length = len(order.items)
    order.items = [item for item in order.items if item.item_id != item_id]
    
    if len(order.items) == original_length:
        raise HTTPException(status_code=404, detail="Item not found in order")

    return yaml.dump({"message": f"Item {item_id} deleted from order {order_id}"}, sort_keys=False)

if __name__ == "__main__":
    # Run with: python main.py  (or use uvicorn directly for production)
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
