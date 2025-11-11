from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date
import yaml

class InventoryItem(BaseModel):
    item_id: int
    name: str
    category: str
    quantity: int = Field(ge=0)  # Ensure quantity is non-negative
    unit_price: float = Field(ge=0.0)  # Ensure price is non-negative
    supplier: str
    restock_date: Optional[date] = None

class Warehouse(BaseModel):
    warehouse_id: str
    name: str
    location: str
    last_updated: date
    inventory: List[InventoryItem] = []

app = FastAPI()

# In-memory warehouse store
warehouses: Dict[str, Warehouse] = {}

# Load warehouses from YAML file
with open('data/warehouse.yaml', 'r') as file:
    data = yaml.safe_load(file)
    
    if not isinstance(data, dict) or 'warehouses' not in data or not isinstance(data['warehouses'], list):
        raise ValueError("Invalid warehouse.yaml format. Expected 'warehouses' list at root level.")
        
    for warehouse_data in data['warehouses']:
        try:
            # Convert inventory items to proper format if present
            if 'inventory' in warehouse_data:
                inventory_items = [InventoryItem(**item) for item in warehouse_data['inventory']]
                warehouse_data['inventory'] = inventory_items
                
            # Create and store warehouse object
            warehouse = Warehouse(**warehouse_data)
            warehouses[warehouse.warehouse_id] = warehouse
        except ValueError as e:
            print(f"Error loading warehouse: {e}")

@app.get("/warehouses", response_class=PlainTextResponse)
async def get_warehouses():
    """
    Retrieve a list of all warehouses in the system.
    
    Returns:
        PlainTextResponse: YAML formatted string containing all warehouse information
    """
    return yaml.dump({"warehouses": [w.model_dump() for w in warehouses.values()]}, sort_keys=False)

@app.get("/warehouses/{warehouse_id}", response_class=PlainTextResponse)
async def get_warehouse(warehouse_id: str):
    """
    Retrieve information about a specific warehouse.
    
    Args:
        warehouse_id (str): The unique identifier of the warehouse
    
    Returns:
        PlainTextResponse: YAML formatted string containing the warehouse information
    
    Raises:
        HTTPException: 404 if warehouse is not found
    """
    if warehouse_id not in warehouses:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return yaml.dump(warehouses[warehouse_id].model_dump(), sort_keys=False)

@app.post("/warehouses", response_class=PlainTextResponse)
async def add_warehouse(request: Request):
    """
    Create a new warehouse in the system.
    
    Args:
        request (Request): FastAPI request object containing YAML formatted warehouse data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming warehouse creation
    
    Raises:
        HTTPException: 400 if YAML is invalid or warehouse ID already exists
    """
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        if data is None:
            raise HTTPException(status_code=400, detail="body must not be empty")
        warehouse = Warehouse(**data)
        if warehouse.warehouse_id in warehouses:
            raise HTTPException(status_code=400, detail="Warehouse ID already exists")
        warehouses[warehouse.warehouse_id] = warehouse
        return yaml.dump({"message": "Warehouse added", "warehouse": warehouse.model_dump()}, sort_keys=False)
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/warehouses/{warehouse_id}", response_class=PlainTextResponse)
async def update_warehouse(warehouse_id: str, request: Request):
    """
    Update an existing warehouse's information.
    
    Args:
        warehouse_id (str): The unique identifier of the warehouse to update
        request (Request): FastAPI request object containing YAML formatted warehouse data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming warehouse update
    
    Raises:
        HTTPException: 404 if warehouse not found, 400 if YAML is invalid or IDs don't match
    """
    if warehouse_id not in warehouses:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        updated_warehouse = Warehouse(**data)
        if updated_warehouse.warehouse_id != warehouse_id:
            raise HTTPException(status_code=400, detail="Warehouse ID in URL does not match payload")
        warehouses[warehouse_id] = updated_warehouse
        return yaml.dump({"message": "Warehouse updated", "warehouse": updated_warehouse.model_dump()}, sort_keys=False)
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/warehouses/{warehouse_id}", response_class=PlainTextResponse)
async def delete_warehouse(warehouse_id: str):
    """
    Delete a warehouse from the system.
    
    Args:
        warehouse_id (str): The unique identifier of the warehouse to delete
    
    Returns:
        PlainTextResponse: YAML formatted string confirming warehouse deletion
    
    Raises:
        HTTPException: 404 if warehouse not found
    """
    if warehouse_id not in warehouses:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    del warehouses[warehouse_id]
    return yaml.dump({"message": f"Warehouse {warehouse_id} deleted"}, sort_keys=False)

# Inventory management within warehouses
@app.get("/warehouses/{warehouse_id}/inventory", response_class=PlainTextResponse)
async def get_warehouse_inventory(warehouse_id: str):
    """
    Retrieve the inventory list for a specific warehouse.
    
    Args:
        warehouse_id (str): The unique identifier of the warehouse
    
    Returns:
        PlainTextResponse: YAML formatted string containing the warehouse's inventory
    
    Raises:
        HTTPException: 404 if warehouse not found
    """
    if warehouse_id not in warehouses:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return yaml.dump({"inventory": [item.model_dump() for item in warehouses[warehouse_id].inventory]}, sort_keys=False)

@app.post("/warehouses/{warehouse_id}/inventory", response_class=PlainTextResponse)
async def add_warehouse_item(warehouse_id: str, request: Request):
    """
    Add a new inventory item to a specific warehouse.
    
    Args:
        warehouse_id (str): The unique identifier of the warehouse
        request (Request): FastAPI request object containing YAML formatted item data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming item addition
    
    Raises:
        HTTPException: 404 if warehouse not found, 400 if YAML is invalid or item ID exists
    """
    if warehouse_id not in warehouses:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        if data is None:
            raise HTTPException(status_code=400, detail="body must not be empty")
        item = InventoryItem(**data)
        warehouse = warehouses[warehouse_id]
        # Check if item already exists
        if any(existing.item_id == item.item_id for existing in warehouse.inventory):
            raise HTTPException(status_code=400, detail="Item ID already exists in this warehouse")
        warehouse.inventory.append(item)
        warehouse.last_updated = date.today()
        return yaml.dump({"message": "Item added", "item": item.model_dump()}, sort_keys=False)
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/warehouses/{warehouse_id}/inventory/{item_id}", response_class=PlainTextResponse)
async def update_warehouse_item(warehouse_id: str, item_id: int, request: Request):
    """
    Update an existing inventory item in a specific warehouse.
    
    Args:
        warehouse_id (str): The unique identifier of the warehouse
        item_id (int): The unique identifier of the item to update
        request (Request): FastAPI request object containing YAML formatted item data
    
    Returns:
        PlainTextResponse: YAML formatted string confirming item update
    
    Raises:
        HTTPException: 404 if warehouse or item not found, 400 if YAML is invalid or IDs don't match
    """
    if warehouse_id not in warehouses:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    warehouse = warehouses[warehouse_id]
    body = await request.body()
    try:
        data = yaml.safe_load(body)
        updated_item = InventoryItem(**data)
        if updated_item.item_id != item_id:
            raise HTTPException(status_code=400, detail="Item ID in URL does not match payload")
        
        for i, item in enumerate(warehouse.inventory):
            if item.item_id == item_id:
                warehouse.inventory[i] = updated_item
                warehouse.last_updated = date.today()
                return yaml.dump({"message": "Item updated", "item": updated_item.model_dump()}, sort_keys=False)
        raise HTTPException(status_code=404, detail="Item not found in warehouse")
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/warehouses/{warehouse_id}/inventory/{item_id}", response_class=PlainTextResponse)
async def delete_warehouse_item(warehouse_id: str, item_id: int):
    """
    Delete an inventory item from a specific warehouse.
    
    Args:
        warehouse_id (str): The unique identifier of the warehouse
        item_id (int): The unique identifier of the item to delete
    
    Returns:
        PlainTextResponse: YAML formatted string confirming item deletion
    
    Raises:
        HTTPException: 404 if warehouse or item not found
    """
    if warehouse_id not in warehouses:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    warehouse = warehouses[warehouse_id]
    original_length = len(warehouse.inventory)
    warehouse.inventory = [item for item in warehouse.inventory if item.item_id != item_id]
    
    if len(warehouse.inventory) == original_length:
        raise HTTPException(status_code=404, detail="Item not found in warehouse")
    
    warehouse.last_updated = date.today()
    return yaml.dump({"message": f"Item {item_id} deleted from warehouse {warehouse_id}"}, sort_keys=False)

if __name__ == "__main__":
    # Run with: python main.py  (or use uvicorn directly for production)
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
