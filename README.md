# ChoreQuest

Gamifizierter Haushalts-Todo-Manager mit Punktesystem, Streaks, Achievements und Home Assistant Integration.

## Features

- **Aufgabenverwaltung** — Wiederkehrende und einmalige Haushalts-Tasks, gruppiert nach Räumen
- **Punktesystem** — Basispunkte mit Raum-Multiplikator, Frühbonus, Streak-Bonus und Raum-Completion-Bonus
- **Streaks** — Aufeinanderfolgende Tage mit erledigten Aufgaben werden belohnt
- **Achievements** — Freischaltbare Erfolge für Meilensteine (erste Aufgabe, 50 Tasks, 7-Tage-Streak, ...)
- **Rangliste** — Gesamt- und Wochen-Leaderboard
- **Home Assistant Integration** — Custom Component mit Sensoren, Todo-Listen und Echtzeit-Webhooks
- **KI-Zusammenfassungen** — Wöchentliche Zusammenfassungen und Vorschläge via Claude AI

## Tech-Stack

| Komponente | Technologie |
|-----------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL 16 |
| Frontend | SvelteKit, TailwindCSS |
| Home Assistant | Custom Integration (Sensoren, Binary Sensoren, Todo) |
| Infrastruktur | Docker Compose, Alembic |
| KI | Anthropic Claude API |

## Voraussetzungen

- Docker und Docker Compose
- Optional: Home Assistant (für HA-Integration)
- Optional: Anthropic Claude API-Key (für KI-Zusammenfassungen)

## Installation

```bash
git clone <repository-url>
cd ChoreQuest
cp .env.example .env
# .env anpassen (API-Key setzen!)
docker compose up --build
```

Das Backend ist unter `http://localhost:8000` erreichbar, das Frontend unter `http://localhost:3000`.

## Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|-------------|----------|
| `CHOREQUEST_DB_PASSWORD` | PostgreSQL-Passwort | `chorequest` |
| `CHOREQUEST_API_KEY` | API-Key für Backend-Zugriff | `changeme` |
| `CHOREQUEST_CLAUDE_API_KEY` | Anthropic API-Key (optional) | — |
| `CHOREQUEST_HA_URL` | Home Assistant URL (optional) | — |
| `CHOREQUEST_HA_WEBHOOK_ID` | Webhook-ID für HA (optional) | — |
| `CHOREQUEST_DEBUG` | Debug-Modus aktivieren | `false` |

## API-Dokumentation

Die interaktive API-Dokumentation (Swagger UI) ist unter `http://localhost:8000/docs` erreichbar.

Alle Endpoints (außer `/api/health`) erfordern einen Bearer Token:

```bash
curl -H "Authorization: Bearer DEIN_API_KEY" http://localhost:8000/api/users
```

### Wichtige Endpoints

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `GET` | `/api/health` | Health Check |
| `GET` | `/api/dashboard` | Kompakte Daten für HA |
| `GET` | `/api/users` | Alle Benutzer |
| `GET` | `/api/rooms` | Alle Räume |
| `GET` | `/api/tasks` | Task-Templates |
| `GET` | `/api/instances/today` | Heutige Aufgaben |
| `POST` | `/api/instances/{id}/complete` | Task abhaken |
| `GET` | `/api/leaderboard` | Rangliste (Gesamt) |
| `GET` | `/api/leaderboard/weekly` | Rangliste (Woche) |
| `GET` | `/api/achievements` | Alle Achievements |
| `POST` | `/api/summaries/generate` | KI-Zusammenfassung generieren |

## Home Assistant Integration

1. `homeassistant/custom_components/chorequest/` nach `config/custom_components/chorequest/` kopieren
2. Home Assistant neustarten
3. Integration hinzufügen: Einstellungen → Geräte & Dienste → Integration hinzufügen → "ChoreQuest"
4. Backend-URL und API-Key eingeben
5. Räume und Benutzer werden automatisch synchronisiert

### Webhook-Benachrichtigungen

Für Echtzeit-Updates (Task erledigt, Achievement freigeschaltet):

1. `CHOREQUEST_HA_URL` und `CHOREQUEST_HA_WEBHOOK_ID` in `.env` setzen
2. Die Webhook-ID wird beim Config Flow automatisch generiert und in `entry.data` gespeichert
3. Events werden als `chorequest_task_completed` und `chorequest_achievement_unlocked` in HA gefeuert

## Entwicklung

### Tests ausführen

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Lokaler Start ohne Docker

```bash
cd backend
pip install -r requirements.txt
export CHOREQUEST_DATABASE_URL=postgresql+asyncpg://chorequest:chorequest@localhost:5432/chorequest
export CHOREQUEST_API_KEY=dev-key
uvicorn app.main:app --reload
```

## Projektstruktur

```
ChoreQuest/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI Entry mit Lifespan
│   │   ├── config.py             # Pydantic Settings
│   │   ├── database.py           # Async SQLAlchemy
│   │   ├── auth.py               # API-Key Auth
│   │   ├── seed.py               # Beispieldaten
│   │   ├── models/               # SQLAlchemy Models
│   │   ├── schemas/              # Pydantic Schemas
│   │   ├── routers/              # API Endpoints
│   │   └── services/             # Business Logic
│   ├── alembic/                  # DB-Migrationen
│   ├── tests/                    # pytest Tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                     # SvelteKit Frontend
├── homeassistant/
│   └── custom_components/
│       └── chorequest/           # HA Custom Integration
├── docker-compose.yml
├── .env.example
└── README.md
```
