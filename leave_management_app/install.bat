@echo off
REM Skrypt instalacyjny dla systemu zarządzania urlopami (Windows)
REM Autor: Leave Management System

echo ================================
echo Leave Management System - Instalacja
echo ================================
echo.

REM Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python nie jest zainstalowany!
    echo Zainstaluj Python 3.8 lub nowszy z: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Znaleziono Python
python --version

REM Utwórz środowisko wirtualne
echo [INFO] Tworzenie srodowiska wirtualnego...
if not exist "venv" (
    python -m venv venv
    echo [INFO] Srodowisko wirtualne utworzone
) else (
    echo [WARN] Srodowisko wirtualne juz istnieje, pomijam...
)

REM Aktywuj środowisko wirtualne
echo [INFO] Aktywacja srodowiska wirtualnego...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Aktualizacja pip...
python -m pip install --upgrade pip --quiet

REM Instaluj zależności
echo [INFO] Instalowanie zaleznosci z requirements.txt...
cd backend
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Blad podczas instalacji zaleznosci
    pause
    exit /b 1
)

echo [INFO] Zaleznosci zainstalowane pomyslnie!

cd ..

REM Utwórz plik .env jeśli nie istnieje
if not exist "backend\.env" (
    echo [INFO] Tworzenie pliku konfiguracyjnego .env...
    copy backend\.env.example backend\.env
    echo [INFO] Plik .env utworzony
    echo [WARN] UWAGA: Zmien SECRET_KEY w pliku backend\.env!
) else (
    echo [WARN] Plik .env juz istnieje, pomijam...
)

REM Inicjalizuj bazę danych
echo [INFO] Inicjalizacja bazy danych...
cd backend
python -c "from app.database import init_db; init_db(); print('Baza danych zainicjalizowana')"
cd ..

echo.
echo ================================
echo [INFO] Instalacja zakonczona pomyslnie!
echo ================================
echo.
echo Aby uruchomic aplikacje:
echo.
echo 1. Aktywuj srodowisko wirtualne:
echo    venv\Scripts\activate.bat
echo.
echo 2. Uruchom serwer:
echo    cd backend
echo    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo 3. Otworz przegladarke:
echo    http://localhost:8000
echo.
echo Domyslne konto administratora:
echo    Username: admin
echo    Password: admin123
echo.
echo WAZNE: Zmien haslo administratora po pierwszym logowaniu!
echo.
echo Konfiguracja email (opcjonalna):
echo    Edytuj plik: backend\.env
echo    Ustaw EMAIL_ENABLED=true i skonfiguruj SMTP
echo.
pause
