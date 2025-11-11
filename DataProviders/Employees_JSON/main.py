from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import json
import os

app = FastAPI(title="Employees Data Provider")

DATA_FILE = os.path.join("data", "employees.json")

# ---------------- Data Persistence ----------------
def load_data() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

employees = load_data()

# ---------------- Pydantic Model ----------------
class Employee(BaseModel):
    first_name: str = Field(..., example="David")
    last_name: str = Field(..., example="Lee")
    role: str = Field(..., example="Analyst")
    department: str = Field(..., example="Finance")
    salary: int = Field(..., gt=0, example=70000)  # must be positive

class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    department: str | None = None
    salary: int | None = Field(None, gt=0)

# ---------------- CRUD ----------------
@app.get("/employees")
def get_employees():
    return employees

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    for emp in employees:
        if emp["id"] == employee_id:
            return emp
    raise HTTPException(status_code=404, detail="Employee not found")

@app.post("/employees")
def create_employee(employee: Employee):
    new_employee = employee.dict()
    new_employee["id"] = max([e["id"] for e in employees] + [0]) + 1
    employees.append(new_employee)
    save_data(employees)
    return new_employee

@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, updated: EmployeeUpdate):
    for i, emp in enumerate(employees):
        if emp["id"] == employee_id:
            updated_data = updated.dict(exclude_unset=True)
            employees[i].update(updated_data)
            save_data(employees)
            return employees[i]
    raise HTTPException(status_code=404, detail="Employee not found")

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    for i, emp in enumerate(employees):
        if emp["id"] == employee_id:
            removed = employees.pop(i)
            save_data(employees)
            return removed
    raise HTTPException(status_code=404, detail="Employee not found")
