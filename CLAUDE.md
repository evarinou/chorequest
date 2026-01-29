# ChoreQuest - Projekt-Kontext für Claude Code

## Projektbeschreibung

Gamifizierter Haushalts-Todo-Manager mit FastAPI Backend, SvelteKit Frontend, Home Assistant Integration und Claude AI für wöchentliche Zusammenfassungen.

## Tech-Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL 16, Pydantic v2, APScheduler
- **Frontend**: SvelteKit, TailwindCSS, @mdi/js (geplant, noch nicht erstellt)
- **Home Assistant**: Custom Integration (geplant, noch nicht erstellt)
- **Infrastruktur**: Docker Compose, Alembic für Migrationen
- **AI**: Anthropic Claude API (claude-haiku-4-5-20250929)

## Projektstruktur

```
ChoreQuest/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI Entry mit Lifespan (auto-create tables + seed)
│   │   ├── config.py         # Pydantic Settings (CHOREQUEST_ Env-Prefix)
│   │   ├── database.py       # Async SQLAlchemy Engine + Session
│   │   ├── auth.py           # API-Key Bearer Token Auth
│   │   ├── seed.py           # Beispieldaten beim ersten Start
│   │   ├── models/           # SQLAlchemy Models
│   │   ├── schemas/          # Pydantic Request/Response Schemas
│   │   ├── routers/          # API Endpoints
│   │   ├── services/         # Business Logic (noch leer)
│   │   └── utils/            # Hilfsfunktionen (noch leer)
│   ├── alembic/              # DB-Migrationen
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml        # Backend + PostgreSQL
├── .env.example
└── NEXT_STEPS.md             # Detaillierter Entwicklungsplan
```

## Konventionen

- **Sprache**: Alle UI-Texte, Kommentare und API-Fehlermeldungen auf Deutsch
- **Timezone**: Europe/Berlin
- **Icons**: Material Design Icons (mdi:) für HA-Kompatibilität
- **Ports**: Backend 8000, Frontend 3000, PostgreSQL 5432
- **Env-Variablen**: Prefix `CHOREQUEST_` (z.B. `CHOREQUEST_API_KEY`)
- **Python**: Async/await, Type Hints, Pydantic v2 Patterns
- **API-Auth**: Bearer Token mit API-Key aus Env

## Räume-Konzept: Sync aus Home Assistant

Räume werden **aus Home Assistant importiert**, nicht manuell in ChoreQuest gepflegt.
So wird doppelte Pflege vermieden.

- Beim Config Flow der HA-Integration werden die HA-Areas (`area_registry`) ausgelesen
- Diese werden automatisch als Räume im Backend via `POST /api/rooms` angelegt
- Die HA-Integration synchronisiert Änderungen (neue Areas, umbenannte Areas)
- ChoreQuest-spezifische Felder (point_multiplier, icon-Override) werden im Backend/Frontend gesetzt
- Das `rooms`-Model hat ein Feld `ha_area_id` (optional) um die Zuordnung zu speichern
- Räume im Frontend werden nur gelesen/konfiguriert, nicht manuell erstellt (das kommt aus HA)
- Fallback: Wenn keine HA-Verbindung besteht, können Räume auch manuell erstellt werden

## Datenbank

PostgreSQL 16 mit async SQLAlchemy. Tabellen:
- `users` - Benutzer mit Gamification-Stats (total_points, weekly_points, streaks)
- `rooms` - Räume mit point_multiplier + `ha_area_id` (Sync mit HA Areas)
- `tasks` - Task-Templates (wiederkehrend: daily/weekly/monthly/once)
- `task_instances` - Konkrete Task-Instanzen mit Status (pending/completed/skipped)
- `task_completions` - Erledigungen mit Punkten
- `achievements` - Achievement-Definitionen (criteria als JSON)
- `user_achievements` - Freigeschaltete Achievements pro User
- `weekly_summaries` - Claude AI Zusammenfassungen

## Seed-Daten

Beim ersten Start werden automatisch erstellt:
- 2 Benutzer: Lukas, Eva
- Räume werden NICHT mehr geseeded (kommen aus HA-Sync)
- Beispiel-Tasks werden erst nach dem ersten Raum-Sync erstellt

## Entwicklungsstand

- [x] Phase 1: Backend-Grundgerüst (CRUD, Auth, Docker)
- [ ] Phase 2: Gamification-Logik (Punkte, Streaks, Achievements, Scheduler)
- [ ] Phase 3: Home Assistant Integration
- [ ] Phase 4: SvelteKit Frontend
- [ ] Phase 5: Claude AI Integration
- [ ] Phase 6: Feinschliff

## Starten

```bash
cp .env.example .env
docker compose up --build
# API-Docs: http://localhost:8000/docs
# Health: http://localhost:8000/api/health
```

## Wichtige API-Endpoints

```
GET    /api/health              # Health Check
GET    /api/dashboard           # Kompakte Daten für HA
GET    /api/users               # Alle Benutzer
GET    /api/rooms               # Alle Räume
GET    /api/tasks               # Task-Templates
GET    /api/instances           # Task-Instanzen (Filter: room, user, status, date)
GET    /api/instances/today     # Heutige Aufgaben
POST   /api/instances/{id}/complete  # Task abhaken {user_id, notes?}
GET    /api/leaderboard         # Rangliste (Gesamt)
GET    /api/leaderboard/weekly  # Rangliste (Woche)
```

Alle Endpoints (außer /api/health) brauchen `Authorization: Bearer <API_KEY>`.
