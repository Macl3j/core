@echo off
REM Skrypt uruchamiający aplikację Leave Management System (Windows)

echo ================================
echo Leave Management System
echo Uruchamianie serwera...
echo ================================
echo.

REM Sprawdź czy środowisko wirtualne istnieje
if not exist "venv" (
    echo [ERROR] Srodowisko wirtualne nie istnieje!
    echo Uruchom najpierw: install.bat
    pause
    exit /b 1
)

REM Aktywuj środowisko wirtualne
call venv\Scripts\activate.bat

REM Przejdź do katalogu backend
cd backend

REM Uruchom serwer
echo [INFO] Uruchamianie serwera na http://localhost:8000
echo.
echo Domyslne konto administratora:
echo   Username: admin
echo   Password: admin123
echo.
echo Dokumentacja API: http://localhost:8000/api/docs
echo.
echo Nacisnij Ctrl+C aby zatrzymac serwer
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
