# Instrukcja Wdrożenia - System Zarządzania Urlopami

Ten dokument opisuje różne sposoby wdrożenia aplikacji Leave Management System.

## 📦 Metody Wdrożenia

### 1. 🐳 Docker (Zalecane dla produkcji)
### 2. 🐍 Instalacja natywna (Python)
### 3. ☁️ Wdrożenie w chmurze

---

## 🐳 Metoda 1: Docker (Zalecane)

Docker to najlepszy sposób na uruchomienie aplikacji - zapewnia izolację, łatwą instalację i przenośność.

### Wymagania
- Docker (https://docs.docker.com/get-docker/)
- Docker Compose (zwykle instalowany z Docker Desktop)

### Instalacja

1. **Sklonuj repozytorium (lub przejdź do katalogu)**
```bash
cd leave_management_app
```

2. **Stwórz plik .env dla konfiguracji**
```bash
cp backend/.env.example .env
```

3. **Edytuj .env i skonfiguruj**
```env
SECRET_KEY=twoj-bardzo-bezpieczny-klucz
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=twoj-email@gmail.com
SMTP_PASSWORD=haslo-aplikacji
```

4. **Zbuduj i uruchom kontenery**
```bash
docker-compose up -d --build
```

5. **Sprawdź logi**
```bash
docker-compose logs -f app
```

6. **Otwórz aplikację**
```
http://localhost:8000
```

### Zarządzanie kontenerem

**Zatrzymaj kontenery:**
```bash
docker-compose down
```

**Restartuj kontenery:**
```bash
docker-compose restart
```

**Zobacz logi:**
```bash
docker-compose logs -f
```

**Wejdź do kontenera:**
```bash
docker-compose exec app bash
```

**Usuń kontenery i dane:**
```bash
docker-compose down -v
```

### Aktualizacja aplikacji

```bash
# Pobierz najnowszy kod
git pull

# Przebuduj kontenery
docker-compose up -d --build

# Sprawdź logi
docker-compose logs -f app
```

---

## 🐍 Metoda 2: Instalacja Natywna (Python)

### Linux / macOS

1. **Uruchom skrypt instalacyjny**
```bash
chmod +x install.sh
./install.sh
```

2. **Uruchom aplikację**
```bash
chmod +x start.sh
./start.sh
```

Lub manualnie:
```bash
# Aktywuj środowisko wirtualne
source venv/bin/activate

# Uruchom serwer
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Windows

1. **Uruchom skrypt instalacyjny**
```cmd
install.bat
```

2. **Uruchom aplikację**
```cmd
start.bat
```

Lub manualnie:
```cmd
REM Aktywuj środowisko wirtualne
venv\Scripts\activate.bat

REM Uruchom serwer
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Manualna instalacja (wszystkie systemy)

```bash
# 1. Utwórz środowisko wirtualne
python3 -m venv venv

# 2. Aktywuj środowisko wirtualne
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate.bat

# 3. Zainstaluj zależności
cd backend
pip install -r requirements.txt

# 4. Skopiuj i edytuj konfigurację
cp .env.example .env
# Edytuj plik .env

# 5. Uruchom serwer
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## ☁️ Metoda 3: Wdrożenie w Chmurze

### Heroku

1. **Utwórz plik `Procfile`**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. **Deploy**
```bash
# Zaloguj się do Heroku
heroku login

# Utwórz aplikację
heroku create nazwa-twojej-aplikacji

# Ustaw zmienne środowiskowe
heroku config:set SECRET_KEY=twoj-secret-key
heroku config:set EMAIL_ENABLED=true
heroku config:set SMTP_HOST=smtp.gmail.com
# itd...

# Deploy
git push heroku main
```

### AWS EC2

1. **Połącz się z instancją EC2**
```bash
ssh -i twoj-klucz.pem ubuntu@adres-ec2
```

2. **Zainstaluj Docker**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
```

3. **Sklonuj repozytorium i uruchom**
```bash
git clone https://github.com/twoj-repo/leave-management-app.git
cd leave-management-app
docker-compose up -d
```

4. **Konfiguruj firewall (Security Group)**
- Otwórz port 8000 dla HTTP

### Digital Ocean / Linode / VPS

1. **Połącz się z serwerem**
```bash
ssh root@adres-serwera
```

2. **Zainstaluj Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Uruchom aplikację**
```bash
git clone https://github.com/twoj-repo/leave-management-app.git
cd leave-management-app
docker-compose up -d
```

### Google Cloud Run

1. **Utwórz plik `cloudbuild.yaml`**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/leave-management', '.']
images:
  - 'gcr.io/$PROJECT_ID/leave-management'
```

2. **Deploy**
```bash
gcloud builds submit --config cloudbuild.yaml
gcloud run deploy leave-management --image gcr.io/$PROJECT_ID/leave-management
```

---

## 🔧 Konfiguracja Produkcyjna

### Baza danych PostgreSQL (zamiast SQLite)

1. **Odkomentuj sekcję PostgreSQL w `docker-compose.yml`**

2. **Zmień `DATABASE_URL` w .env**
```env
DATABASE_URL=postgresql://leave_user:haslo@postgres:5432/leave_management
```

### Reverse Proxy (Nginx)

**Utwórz `nginx.conf`**
```nginx
server {
    listen 80;
    server_name twoja-domena.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### SSL/HTTPS (Let's Encrypt)

```bash
# Zainstaluj certbot
sudo apt install certbot python3-certbot-nginx

# Wygeneruj certyfikat
sudo certbot --nginx -d twoja-domena.com
```

### Systemd Service (Linux)

**Utwórz `/etc/systemd/system/leave-management.service`**
```ini
[Unit]
Description=Leave Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/leave-management-app/backend
Environment="PATH=/opt/leave-management-app/venv/bin"
ExecStart=/opt/leave-management-app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Uruchom service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable leave-management
sudo systemctl start leave-management
sudo systemctl status leave-management
```

---

## 📊 Monitoring i Logi

### Logi Docker
```bash
docker-compose logs -f app
```

### Logi natywne
```bash
# Przekieruj stdout do pliku
python -m uvicorn app.main:app --log-config logging.json > app.log 2>&1
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

---

## 🔒 Bezpieczeństwo

### Checklist przed produkcją:

- [ ] Zmień `SECRET_KEY` na losową wartość (min. 32 znaki)
- [ ] Zmień domyślne hasło administratora
- [ ] Ustaw `DATABASE_URL` na PostgreSQL (nie SQLite)
- [ ] Włącz HTTPS (SSL/TLS)
- [ ] Skonfiguruj firewall (tylko porty 80, 443)
- [ ] Ustaw CORS tylko dla swojej domeny
- [ ] Włącz rate limiting
- [ ] Regularne backupy bazy danych
- [ ] Monitoring i alerty

### Backup bazy danych

**Docker SQLite:**
```bash
docker cp leave_management_app:/app/data/leave_management.db ./backup_$(date +%Y%m%d).db
```

**Docker PostgreSQL:**
```bash
docker-compose exec postgres pg_dump -U leave_user leave_management > backup_$(date +%Y%m%d).sql
```

---

## 🚀 Optymalizacja Wydajności

### Gunicorn (zamiast Uvicorn)

```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Redis Cache (opcjonalnie)

Dodaj do `docker-compose.yml`:
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

---

## 📞 Wsparcie

W razie problemów:
1. Sprawdź logi: `docker-compose logs -f`
2. Sprawdź dokumentację API: http://localhost:8000/api/docs
3. Sprawdź health endpoint: http://localhost:8000/api/health

---

**Powodzenia z wdrożeniem! 🎉**
