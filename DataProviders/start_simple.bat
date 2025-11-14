@ECHO OFF
SETLOCAL EnableDelayedExpansion

ECHO ========================================
ECHO Starting DataProviders (Simplified)
ECHO ========================================
ECHO.

REM Start Python services (these always work)
ECHO Starting Python services...

REM Employees_JSON
start "Employees_JSON" cmd /k "cd Employees_JSON && uvicorn main:app --port 8001"

REM Inventory_JSON
start "Inventory_JSON" cmd /k "cd Inventory_JSON && uvicorn main:app --port 8002"

REM Distribution_YAML
start "Distribution_YAML" cmd /k "cd Distribution_YAML && uvicorn main:app --port 8003"

REM Warehouse_YAML
start "Warehouse_YAML" cmd /k "cd Warehouse_YAML && uvicorn main:app --port 8004"

ECHO.
ECHO Python services started!
ECHO.
ECHO Press any key to also start Java and Go services...
ECHO (Or close this if you only want to test Python-based features)
pause >nul

REM Go service
ECHO Starting Go service...
start "National_Weather_XML" cmd /k "cd National_Weather_XML\cmd\server && go run main.go"

REM Spring Boot services (if already built)
IF EXIST "Transport_CSV\target\transport-service-0.0.1-SNAPSHOT.jar" (
    ECHO Starting Transport service...
    start "Transport_CSV" cmd /k "cd Transport_CSV && mvn spring-boot:run"
) ELSE (
    ECHO Warning: Transport service JAR not found, skipping...
)

IF EXIST "Finances_CSV\target\finances-service-0.0.1-SNAPSHOT.jar" (
    ECHO Starting Finances service...
    start "Finances_CSV" cmd /k "cd Finances_CSV && mvn spring-boot:run"
) ELSE (
    ECHO Warning: Finances service JAR not found, skipping...
)

IF EXIST "Healthcare_XML\target\patient-soap-1.0.0.jar" (
    ECHO Starting Healthcare service...
    start "Healthcare_XML" cmd /k "cd Healthcare_XML && java -jar target\patient-soap-1.0.0.jar"
) ELSE (
    ECHO Warning: Healthcare service JAR not found, skipping...
)

ECHO.
ECHO ========================================
ECHO Services Started!
ECHO ========================================
ECHO.
ECHO Python services (guaranteed):
ECHO   - Employees_JSON: http://localhost:8001
ECHO   - Inventory_JSON: http://localhost:8002
ECHO   - Distribution_YAML: http://localhost:8003
ECHO   - Warehouse_YAML: http://localhost:8004
ECHO.
ECHO Other services (if available):
ECHO   - National_Weather_XML: http://localhost:8081
ECHO   - Transport_CSV: http://localhost:8084
ECHO   - Finances_CSV: http://localhost:8085
ECHO   - Healthcare_XML: http://localhost:8082
ECHO.
ECHO You can now test the WITHOUT DataFusion frontend!
ECHO.

ENDLOCAL

