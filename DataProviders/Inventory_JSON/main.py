from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import json
import os

app = FastAPI(title="Inventory Data Provider")

DATA_FILE = os.path.join("data", "inventory.json")

# ---------------- Data Persistence ----------------
def load_data() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

inventory = load_data()

# ---------------- Pydantic Models ----------------
class InventoryItem(BaseModel):
    name: str = Field(..., example="Laptop")
    category: str = Field(..., example="Electronics")
    quantity: int = Field(..., ge=0, example=50)   # must be >= 0
    price: float = Field(..., gt=0, example=999.99)  # must be > 0

class InventoryItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    quantity: int | None = Field(None, ge=0)
    price: float | None = Field(None, gt=0)

# ---------------- CRUD ----------------
@app.get("/inventory")
def get_inventory():
    return inventory

@app.get("/inventory/{item_id}")
def get_item(item_id: int):
    for item in inventory:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/inventory")
def create_item(item: InventoryItem):
    new_item = item.dict()
    new_item["id"] = max([i["id"] for i in inventory] + [100]) + 1
    inventory.append(new_item)
    save_data(inventory)
    return new_item

@app.put("/inventory/{item_id}")
def update_item(item_id: int, updated: InventoryItemUpdate):
    for i, item in enumerate(inventory):
        if item["id"] == item_id:
            updated_data = updated.dict(exclude_unset=True)
            inventory[i].update(updated_data)
            save_data(inventory)
            return inventory[i]
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/inventory/{item_id}")
def delete_item(item_id: int):
    for i, item in enumerate(inventory):
        if item["id"] == item_id:
            removed = inventory.pop(i)
            save_data(inventory)
            return removed
    raise HTTPException(status_code=404, detail="Item not found")
