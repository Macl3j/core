#!/bin/bash

# Skrypt instalacyjny dla systemu zarządzania urlopami
# Autor: Leave Management System
# Opis: Automatyczna instalacja i konfiguracja aplikacji

set -e

echo "================================"
echo "Leave Management System - Instalacja"
echo "================================"
echo ""

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funkcja do wyświetlania komunikatów
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    error "Python 3 nie jest zainstalowany!"
    echo "Zainstaluj Python 3.8 lub nowszy: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
info "Znaleziono Python $PYTHON_VERSION"

# Sprawdź wersję Python
if [ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]; then
    error "Wymagany Python 3.8 lub nowszy!"
    exit 1
fi

# Utwórz środowisko wirtualne
info "Tworzenie środowiska wirtualnego..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    info "Środowisko wirtualne utworzone"
else
    warn "Środowisko wirtualne już istnieje, pomijam..."
fi

# Aktywuj środowisko wirtualne
info "Aktywacja środowiska wirtualnego..."
source venv/bin/activate

# Upgrade pip
info "Aktualizacja pip..."
pip install --upgrade pip > /dev/null 2>&1

# Instaluj zależności
info "Instalowanie zależności z requirements.txt..."
cd backend
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    info "Zależności zainstalowane pomyślnie!"
else
    error "Błąd podczas instalacji zależności"
    exit 1
fi

cd ..

# Utwórz plik .env jeśli nie istnieje
if [ ! -f "backend/.env" ]; then
    info "Tworzenie pliku konfiguracyjnego .env..."
    cp backend/.env.example backend/.env

    # Generuj losowy SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    # Podmień SECRET_KEY w pliku .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-change-this-in-production-use-random-string/$SECRET_KEY/" backend/.env
    else
        # Linux
        sed -i "s/your-secret-key-change-this-in-production-use-random-string/$SECRET_KEY/" backend/.env
    fi

    info "Plik .env utworzony z losowym SECRET_KEY"
else
    warn "Plik .env już istnieje, pomijam..."
fi

# Inicjalizuj bazę danych
info "Inicjalizacja bazy danych..."
cd backend
python3 -c "from app.database import init_db; init_db(); print('Baza danych zainicjalizowana')"
cd ..

echo ""
echo "================================"
info "Instalacja zakończona pomyślnie!"
echo "================================"
echo ""
echo "Aby uruchomić aplikację:"
echo ""
echo "1. Aktywuj środowisko wirtualne:"
echo "   source venv/bin/activate"
echo ""
echo "2. Uruchom serwer:"
echo "   cd backend"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "3. Otwórz przeglądarkę:"
echo "   http://localhost:8000"
echo ""
echo "Domyślne konto administratora:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "WAŻNE: Zmień hasło administratora po pierwszym logowaniu!"
echo ""
echo "Konfiguracja email (opcjonalna):"
echo "   Edytuj plik: backend/.env"
echo "   Ustaw EMAIL_ENABLED=true i skonfiguruj SMTP"
echo ""
