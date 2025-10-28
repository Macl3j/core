#!/bin/bash

# Skrypt uruchamiający aplikację Leave Management System

echo "================================"
echo "Leave Management System"
echo "Uruchamianie serwera..."
echo "================================"
echo ""

# Sprawdź czy środowisko wirtualne istnieje
if [ ! -d "venv" ]; then
    echo "[ERROR] Środowisko wirtualne nie istnieje!"
    echo "Uruchom najpierw: ./install.sh"
    exit 1
fi

# Aktywuj środowisko wirtualne
source venv/bin/activate

# Przejdź do katalogu backend
cd backend

# Uruchom serwer
echo "[INFO] Uruchamianie serwera na http://localhost:8000"
echo ""
echo "Domyślne konto administratora:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Dokumentacja API: http://localhost:8000/api/docs"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać serwer"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
