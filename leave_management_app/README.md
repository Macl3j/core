# System Zarządzania Urlopami

Nowoczesna aplikacja webowa do zarządzania urlopami w organizacji, zbudowana z użyciem FastAPI (backend) i vanilla JavaScript (frontend).

## 🚀 Funkcjonalności

### Dla pracowników:
- ✅ Składanie wniosków urlopowych (różne typy: wypoczynkowy, zwolnienie, bezpłatny, etc.)
- ✅ Przeglądanie historii własnych wniosków
- ✅ Anulowanie wniosków oczekujących
- ✅ Dashboard z statystykami (pozostałe dni urlopu, zwolnienia)
- ✅ Monitorowanie statusu wniosków
- ✅ **Powiadomienia email** o zatwierdzeniu/odrzuceniu wniosku
- ✅ **Eksport do kalendarza** (format iCal/ICS) - integracja z Google Calendar, Outlook, Apple Calendar
- ✅ **Raport osobisty PDF** - podsumowanie urlopów za rok

### Dla managerów:
- ✅ Zatwierdzanie/odrzucanie wniosków podwładnych
- ✅ Przeglądanie wszystkich wniosków zespołu
- ✅ Dashboard z statystykami zespołu
- ✅ Zarządzanie podwładnymi
- ✅ **Powiadomienia email** o nowych wnioskach od podwładnych
- ✅ **Eksport kalendarza zespołu** - przeglądaj urlopy całego zespołu
- ✅ **Raporty zespołu** - CSV, Excel, PDF z danymi zespołu

### Dla administratorów:
- ✅ Pełny dostęp do wszystkich wniosków
- ✅ Zarządzanie użytkownikami
- ✅ Globalne statystyki organizacji
- ✅ Konfiguracja limitów urlopowych
- ✅ **Raporty organizacji** - eksport wszystkich danych do CSV/Excel/PDF
- ✅ **Kalendarz globalny** - urlopy całej organizacji

## 🛠️ Technologie

**Backend:**
- FastAPI - nowoczesny framework Python do tworzenia API
- SQLAlchemy - ORM do obsługi bazy danych
- Pydantic - walidacja danych
- JWT - bezpieczna autentykacja
- Uvicorn - serwer ASGI
- iCalendar - generowanie plików kalendarza
- ReportLab & OpenPyXL - generowanie raportów PDF/Excel
- SMTP - wysyłanie powiadomień email

**Frontend:**
- Vanilla JavaScript (bez frameworków)
- HTML5/CSS3
- Responsywny design

**Baza danych:**
- SQLite (domyślnie, gotowe do zmiany na PostgreSQL/MySQL)

**Integracje:**
- Kalendarz (iCal/ICS) - Google Calendar, Outlook, Apple Calendar
- Email (SMTP) - Gmail, Outlook, SendGrid, itp.

## 📋 Wymagania

- Python 3.8 lub nowszy
- pip (menedżer pakietów Python)

## 🚀 Instalacja i uruchomienie

### 1. Sklonuj repozytorium (lub przejdź do katalogu)

```bash
cd leave_management_app
```

### 2. Utwórz i aktywuj środowisko wirtualne

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Zainstaluj zależności

```bash
cd backend
pip install -r requirements.txt
```

### 4. (Opcjonalnie) Skonfiguruj zmienne środowiskowe

Skopiuj plik `.env.example` do `.env` i dostosuj konfigurację:

```bash
cp .env.example .env
```

Edytuj `.env` i zmień SECRET_KEY na losowy ciąg znaków:

```env
SECRET_KEY=twoj-bardzo-bezpieczny-losowy-klucz-tutaj
DATABASE_URL=sqlite:///./leave_management.db
```

### 5. Uruchom aplikację

Z katalogu `backend/`:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Lub bezpośrednio:

```bash
python -m app.main
```

### 6. Otwórz aplikację w przeglądarce

```
http://localhost:8000
```

## 👤 Domyślne konto administratora

Po pierwszym uruchomieniu aplikacji zostanie automatycznie utworzone konto administratora:

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **WAŻNE:** Zmień hasło po pierwszym zalogowaniu!

## 📖 Dokumentacja API

Aplikacja automatycznie generuje interaktywną dokumentację API:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

## 🗂️ Struktura projektu

```
leave_management_app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Główna aplikacja FastAPI
│   │   ├── database.py          # Konfiguracja bazy danych
│   │   ├── models.py            # Modele SQLAlchemy
│   │   ├── schemas.py           # Schematy Pydantic
│   │   ├── auth.py              # Autentykacja JWT
│   │   └── routers/
│   │       ├── auth.py          # Endpoints autentykacji
│   │       ├── users.py         # Endpoints użytkowników
│   │       └── leaves.py        # Endpoints wniosków urlopowych
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── css/
│   │   └── style.css            # Style aplikacji
│   ├── js/
│   │   └── api.js               # Klient API
│   ├── index.html               # Strona główna
│   ├── login.html               # Strona logowania
│   └── dashboard.html           # Dashboard
└── README.md
```

## 🔐 Bezpieczeństwo

- Hasła są hashowane za pomocą bcrypt
- Autentykacja oparta na JWT tokens
- Tokeny przechowywane w localStorage
- Role-based access control (RBAC)
- Walidacja danych na poziomie API

## 🗄️ Baza danych

### SQLite (domyślnie)
Aplikacja domyślnie używa SQLite - baza danych jest tworzona automatycznie w pliku `leave_management.db`.

### Migracja na PostgreSQL

1. Zainstaluj psycopg2:
```bash
pip install psycopg2-binary
```

2. Zmień DATABASE_URL w `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/leave_management
```

3. Utwórz bazę danych:
```sql
CREATE DATABASE leave_management;
```

### Migracja na MySQL

1. Zainstaluj PyMySQL:
```bash
pip install pymysql
```

2. Zmień DATABASE_URL w `.env`:
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/leave_management
```

## 📧 Konfiguracja powiadomień email

System może wysyłać automatyczne powiadomienia email o:
- Nowych wnioskach urlopowych (do managerów)
- Zatwierdzeniu wniosku (do pracownika)
- Odrzuceniu wniosku (do pracownika)

### Włączanie powiadomień email

1. Skopiuj plik `.env.example` do `.env`:
```bash
cp backend/.env.example backend/.env
```

2. Edytuj `.env` i skonfiguruj SMTP:

```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=twoj-email@gmail.com
SMTP_PASSWORD=twoje-haslo-aplikacji
SMTP_FROM_EMAIL=noreply@twojafirma.com
SMTP_FROM_NAME=System Zarządzania Urlopami
```

### Konfiguracja dla popularnych dostawców

**Gmail:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=twoj-email@gmail.com
SMTP_PASSWORD=haslo-aplikacji
```
*Uwaga: Gmail wymaga "hasła aplikacji" zamiast zwykłego hasła. Wygeneruj je tutaj: https://support.google.com/accounts/answer/185833*

**Outlook/Hotmail:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=twoj-email@outlook.com
SMTP_PASSWORD=twoje-haslo
```

**Office365:**
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=twoj-email@twojafirma.com
SMTP_PASSWORD=twoje-haslo
```

**SendGrid (zalecane dla produkcji):**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=twoj-api-key-z-sendgrid
```

### Testowanie powiadomień

Powiadomienia są wysyłane automatycznie gdy:
1. Pracownik składa nowy wniosek → email do managera
2. Manager zatwierdza wniosek → email do pracownika
3. Manager odrzuca wniosek → email do pracownika

Jeśli `EMAIL_ENABLED=false`, system będzie tylko logował informacje o emailach w konsoli bez ich wysyłania.

## 📅 Eksport do kalendarza

System umożliwia eksport urlopów do formatu iCal/ICS, który można zaimportować do:

### Google Calendar
1. Kliknij "Eksportuj do kalendarza" w dashboardzie
2. Pobierz plik .ics
3. Otwórz Google Calendar
4. Kliknij "+ Inny kalendarz" → "Importuj"
5. Wybierz pobrany plik .ics

### Outlook
1. Pobierz plik .ics
2. Otwórz Outlook
3. Plik → Otwórz i eksportuj → Importuj/Eksportuj
4. Wybierz "Importuj plik iCalendar (.ics)"

### Apple Calendar
1. Pobierz plik .ics
2. Kliknij dwukrotnie na plik
3. Kalendarz automatycznie zaimportuje wydarzenia

## 📊 Raporty i eksport danych

System oferuje różne formaty eksportu danych:

### Dla wszystkich użytkowników:
- **Eksport do kalendarza (ICS)** - własne urlopy
- **Podsumowanie PDF** - raport roczny z wykorzystaniem urlopów

### Dla managerów i administratorów:
- **CSV** - dane tabelaryczne do Excel/arkuszy kalkulacyjnych
- **Excel (XLSX)** - sformatowane raporty z kolorami statusów
- **PDF** - profesjonalne raporty z podsumowaniami
- **Kalendarz zespołu** - urlopy całego zespołu w formacie ICS

### Generowanie raportów:

1. Przejdź do sekcji "Eksport i raporty" w dashboardzie
2. Wybierz odpowiedni format:
   - **CSV** - najlepszydo dalszej obróbki danych
   - **Excel** - dla ładnych tabel z formatowaniem
   - **PDF** - dla prezentacji i archiwizacji
3. Raport zostanie pobrany automatycznie

## 📝 Użytkowanie

### Rejestracja nowego użytkownika

1. Przejdź do strony logowania
2. Kliknij "Zarejestruj się"
3. Wypełnij formularz rejestracyjny
4. Nowi użytkownicy domyślnie mają rolę "employee"

### Składanie wniosku urlopowego

1. Zaloguj się do systemu
2. Kliknij "Nowy wniosek urlopowy"
3. Wybierz typ urlopu
4. Wybierz daty rozpoczęcia i zakończenia
5. (Opcjonalnie) Dodaj powód
6. Kliknij "Wyślij wniosek"

### Zatwierdzanie wniosków (dla managerów)

1. Kliknij "Wnioski do zatwierdzenia"
2. Przejrzyj szczegóły wniosku
3. Kliknij "Zatwierdź" lub "Odrzuć"
4. Przy odrzuceniu podaj powód

## 🎯 Role użytkowników

### Employee (Pracownik)
- Może składać własne wnioski urlopowe
- Widzi tylko własne wnioski
- Może anulować wnioski oczekujące

### Manager
- Wszystkie uprawnienia Employee
- Zatwierdza/odrzuca wnioski podwładnych
- Widzi wnioski całego zespołu
- Dostęp do statystyk zespołu

### Admin (Administrator)
- Wszystkie uprawnienia Manager
- Pełny dostęp do wszystkich wniosków
- Zarządzanie użytkownikami
- Zmiana ról i limitów urlopowych

## 🐛 Rozwiązywanie problemów

### Port już zajęty
Jeśli port 8000 jest zajęty, uruchom aplikację na innym porcie:
```bash
python -m uvicorn app.main:app --reload --port 8080
```

### Błąd importu modułów
Upewnij się, że jesteś w katalogu `backend/` i środowisko wirtualne jest aktywne.

### Brak modułu 'app'
Uruchom aplikację z katalogu `backend/` używając:
```bash
python -m uvicorn app.main:app --reload
```

## 🔄 Aktualizacje i rozwój

### Dodawanie nowych typów urlopów

Edytuj plik `backend/app/models.py`:
```python
class LeaveType(str, Enum):
    # Dodaj nowy typ tutaj
    NEW_TYPE = "new_type"
```

### Zmiana limitów urlopowych

Limity można zmieniać przez:
1. API endpoint (PUT /api/users/{user_id})
2. Bezpośrednio w bazie danych
3. Podczas tworzenia użytkownika

## 📊 Statystyki i raporty

Dashboard automatycznie wyświetla:
- Pozostałe dni urlopu (wypoczynkowego i zwolnienia)
- Liczba wniosków oczekujących
- Liczba zatwierdzonych urlopów w bieżącym roku
- Nadchodzące urlopy

## 🤝 Wkład i rozwój

Projekt jest otwarty na Pull Requests i sugestie ulepszeń!

## 📄 Licencja

MIT License - możesz swobodnie używać, modyfikować i dystrybuować tę aplikację.

## 📞 Wsparcie

W razie problemów lub pytań:
1. Sprawdź dokumentację API: http://localhost:8000/api/docs
2. Przejrzyj logi aplikacji w konsoli
3. Sprawdź plik bazy danych (leave_management.db)

## ✨ Przyszłe funkcjonalności

Zaimplementowane w najnowszej wersji:
- [x] Integracja z kalendarzem (Google Calendar, Outlook, Apple Calendar) - format iCal/ICS
- [x] Powiadomienia email (SMTP)
- [x] Export danych do Excel/CSV/PDF
- [x] Raporty dla managerów i administratorów

Planowane rozszerzenia:
- [ ] Zaawansowane raporty i wykresy (wizualizacje)
- [ ] Multi-tenant support (wiele organizacji)
- [ ] API webhooks dla integracji z innymi systemami
- [ ] Moduł planowania urlopów zespołu (konflikt urlopów)
- [ ] Historia zmian wniosków (audit log)
- [ ] Dwuetapowa akceptacja (manager + HR)
- [ ] Dni wolne i święta (automatyczne wykluczanie)
- [ ] Limity zespołowe (max X osób na urlop jednocześnie)
- [ ] Integracja z Active Directory / LDAP
- [ ] Aplikacja mobilna (PWA)

---

**Dziękujemy za korzystanie z systemu zarządzania urlopami!** 🎉
