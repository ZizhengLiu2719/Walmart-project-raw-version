@ECHO OFF
SETLOCAL EnableDelayedExpansion

FOR /F "tokens=5" %%A IN ('netstat -ano ^| findstr :4000 ^| findstr LISTENING 2^>nul') DO taskkill /PID %%A /F >nul 2>&1
FOR /F "tokens=5" %%A IN ('netstat -ano ^| findstr :8501 ^| findstr LISTENING 2^>nul') DO taskkill /PID %%A /F >nul 2>&1

timeout /t 2 /nobreak >nul

cd DataProviders/
start "Data Providers" cmd /k "python build.py"
cd ..

timeout /t 3 /nobreak >nul

cd DataFusion/
start "DataFusion" cmd /k "npm run dev"
cd ..

timeout /t 5 /nobreak >nul

cd Frontend_Demo/
start "Frontend" cmd /k "streamlit run main.py"
cd ..

ENDLOCAL