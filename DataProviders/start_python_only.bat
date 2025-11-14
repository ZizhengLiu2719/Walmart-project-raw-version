@ECHO OFF
ECHO ========================================
ECHO Starting Python DataProviders Only
ECHO ========================================
ECHO.

REM Check if virtual environment exists
IF EXIST .venv (
    ECHO Activating virtual environment...
    CALL .venv\Scripts\activate.bat
) ELSE (
    ECHO No virtual environment found, using global Python
)

ECHO.
ECHO Starting 4 Python services...
ECHO.

REM Start Employees_JSON (Port 8001)
ECHO [1/4] Starting Employees_JSON on port 8001...
start "Employees_JSON" cmd /k "cd Employees_JSON && uvicorn main:app --port 8001"
timeout /t 2 /nobreak >nul

REM Start Inventory_JSON (Port 8002)
ECHO [2/4] Starting Inventory_JSON on port 8002...
start "Inventory_JSON" cmd /k "cd Inventory_JSON && uvicorn main:app --port 8002"
timeout /t 2 /nobreak >nul

REM Start Distribution_YAML (Port 8003)
ECHO [3/4] Starting Distribution_YAML on port 8003...
start "Distribution_YAML" cmd /k "cd Distribution_YAML && uvicorn main:app --port 8003"
timeout /t 2 /nobreak >nul

REM Start Warehouse_YAML (Port 8004)
ECHO [4/4] Starting Warehouse_YAML on port 8004...
start "Warehouse_YAML" cmd /k "cd Warehouse_YAML && uvicorn main:app --port 8004"
timeout /t 2 /nobreak >nul

ECHO.
ECHO ========================================
ECHO All 4 Python services started!
ECHO ========================================
ECHO.
ECHO Service URLs:
ECHO   - Employees:    http://localhost:8001/employees
ECHO   - Inventory:    http://localhost:8002/inventory
ECHO   - Distribution: http://localhost:8003/orders
ECHO   - Warehouse:    http://localhost:8004/warehouses
ECHO.
ECHO Check each window for "Uvicorn running on..." message
ECHO Press Ctrl+C in each window to stop services
ECHO.
PAUSE

